import React, { useState, useRef, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from "recharts";

import "./App.css";

function App() {

  const [video, setVideo] = useState(null);
  const [videoURL, setVideoURL] = useState(null);
  const [context, setContext] = useState("office");

  const [dataPoints, setDataPoints] = useState([]);
  const [threshold, setThreshold] = useState(null);

  const [alertActive, setAlertActive] = useState(false);
  const [alarmEnabled, setAlarmEnabled] = useState(true);
  const [borderEnabled, setBorderEnabled] = useState(true);

  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const alarmRef = useRef(null);
  const dropZoneRef = useRef(null);

  // Initialize audio only once
  useEffect(() => {
    alarmRef.current = new Audio("/alarm.mp3");
    alarmRef.current.loop = true;
    
    return () => {
      if (alarmRef.current) {
        alarmRef.current.pause();
        alarmRef.current = null;
      }
    };
  }, []);

  // Handle alarm play/pause
  useEffect(() => {
    if (!alarmRef.current) return;

    if (alertActive && alarmEnabled) {
      alarmRef.current.play().catch((err) => {
        console.log("Audio play failed:", err);
      });
    } else {
      alarmRef.current.pause();
      alarmRef.current.currentTime = 0;
    }
  }, [alertActive, alarmEnabled]);

  // Mouse follower effect
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Handle file selection
  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('video/')) {
      setVideo(file);
      setVideoURL(URL.createObjectURL(file));
    } else if (file) {
      alert("Please select a valid video file");
    }
  };

  // Drag and drop handlers
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (dropZoneRef.current && !dropZoneRef.current.contains(e.relatedTarget)) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  // Handle upload
  const handleUpload = () => {
    if (!video) {
      alert("Please select a video");
      return;
    }

    setDataPoints([]);
    setThreshold(null);
    setAlertActive(false);
    setIsProcessing(true);

    const formData = new FormData();
    formData.append("video", video);
    formData.append("context", context);

    fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData
    }).then(response => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      function readStream() {
        reader.read().then(({ done, value }) => {
          if (done) {
            setAlertActive(false);
            return;
          }

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          lines.forEach(line => {
            if (line.startsWith("data:")) {
              const jsonStr = line.replace("data:", "");
              const parsed = JSON.parse(jsonStr);

              if (parsed.type === "meta") {
                setThreshold(parsed.threshold);
              }

              if (parsed.type === "point") {
                // Stop loading spinner on first data point
                setIsProcessing(false);
                
                setAlertActive(parsed.alert);
                setDataPoints(prev => {
                  const updated = [...prev, parsed];
                  return updated.slice(-50);
                });
              }
            }
          });

          readStream();
        });
      }

      readStream();
    }).catch(error => {
      console.error("Upload failed:", error);
      setIsProcessing(false);
      alert("Upload failed. Please try again.");
    });
  };

  // Toggle alarm function
  const toggleAlarm = () => {
    setAlarmEnabled(prev => {
      const newValue = !prev;
      
      if (!newValue && alarmRef.current) {
        alarmRef.current.pause();
        alarmRef.current.currentTime = 0;
      }
      
      return newValue;
    });
  };

  // Export as CSV function
  const exportCSV = () => {
    const headers = ['Index', 'Time (s)', 'Score', 'Status', 'Is Anomaly', 'Is Alert'];
    const rows = dataPoints.map((point, index) => [
      index + 1,
      point.time,
      point.score,
      point.alert ? "ALERT" : point.anomaly ? "ANOMALY" : "NORMAL",
      point.anomaly ? "Yes" : "No",
      point.alert ? "Yes" : "No"
    ]);

    // Add summary at the end
    const totalPoints = dataPoints.length;
    const anomalies = dataPoints.filter(d => d.anomaly).length;
    const alerts = dataPoints.filter(d => d.alert).length;
    const normalPoints = dataPoints.filter(d => !d.anomaly && !d.alert).length;

    const summaryRows = [
      [],
      ['--- SUMMARY ---'],
      ['Video Name', video?.name || 'Unknown'],
      ['Context', context],
      ['Threshold', threshold || 'N/A'],
      ['Total Points', totalPoints],
      ['Anomalies', anomalies],
      ['Alerts', alerts],
      ['Normal Points', normalPoints],
      ['Normal Rate', totalPoints > 0 ? Math.round((normalPoints / totalPoints) * 100) + '%' : '0%'],
      ['Generated At', new Date().toLocaleString()]
    ];

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(',')),
      ...summaryRows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `anomaly-report-${new Date().toISOString().slice(0, 10)}-${Date.now()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {/* Alert Border Overlay */}
      {alertActive && borderEnabled && (
        <div className="alert-border-overlay">
          <div className="alert-border-top"></div>
          <div className="alert-border-right"></div>
          <div className="alert-border-bottom"></div>
          <div className="alert-border-left"></div>
          <div className="alert-corner alert-corner-tl"></div>
          <div className="alert-corner alert-corner-tr"></div>
          <div className="alert-corner alert-corner-bl"></div>
          <div className="alert-corner alert-corner-br"></div>
        </div>
      )}

      {/* Animated Background */}
      <div className="animated-bg">
        <div className="gradient-sphere sphere-1"></div>
        <div className="gradient-sphere sphere-2"></div>
        <div className="gradient-sphere sphere-3"></div>
        <div className="gradient-sphere sphere-4"></div>
        <div 
          className="mouse-follower"
          style={{
            left: `${mousePosition.x}%`,
            top: `${mousePosition.y}%`
          }}
        ></div>
      </div>

      {/* Floating Particles */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${10 + Math.random() * 20}s`
          }}></div>
        ))}
      </div>

      <div className="app-container">

        {/* Header */}
        <div className="header-section">
          <h1 className="title">
            <span className="title-gradient">Video Anomaly</span>
            <span className="title-highlight">Detection</span>
          </h1>
        </div>

        {/* Controls Panel */}
        <div className="controls-card">
          <div className="controls">

            {/* Drag and Drop Zone */}
            <div className="input-group">
              <label className="input-label">
                <span className="label-icon">📁</span>
                Select Video
              </label>
              <div 
                ref={dropZoneRef}
                className={`file-drop-zone ${isDragging ? 'dragging' : ''} ${video ? 'has-file' : ''}`}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  accept="video/*"
                  id="video-input"
                  onChange={(e) => {
                    const file = e.target.files[0];
                    handleFileSelect(file);
                  }}
                />
                <label htmlFor="video-input" className="file-input-label">
                  {isDragging ? (
                    <>
                      <span className="drop-icon">📥</span>
                      <span className="drop-text">Drop video here</span>
                    </>
                  ) : video ? (
                    <>
                      <span className="file-icon">🎬</span>
                      <span className="file-name">{video.name}</span>
                    </>
                  ) : (
                    <>
                      <span className="upload-icon">⬆️</span>
                      <span className="upload-text">
                        <span className="primary-text">Click to upload</span>
                        <span className="secondary-text">or drag and drop</span>
                      </span>
                    </>
                  )}
                </label>
              </div>
            </div>

            <div className="input-group">
              <label className="input-label">
                <span className="label-icon">🎯</span>
                Context
              </label>
              <div className="select-wrapper">
                <select
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  disabled={isProcessing}
                >
                  <option value="office">🏢 Office</option>
                  <option value="street_1">🛣️ Street</option>
                  <option value="highway_1">🚗 Highway</option>
                </select>
                <span className="select-arrow">▼</span>
              </div>
            </div>

            <button 
              className={`btn btn-primary ${isProcessing ? 'processing' : ''}`} 
              onClick={handleUpload}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <span className="spinner"></span>
                  <span className="btn-text">Analyzing...</span>
                </>
              ) : (
                <>
                  <span className="btn-icon">🚀</span>
                  <span className="btn-text">Analyze Video</span>
                  <span className="btn-shine"></span>
                </>
              )}
            </button>

            <button
              className={`btn ${alarmEnabled ? 'btn-danger' : 'btn-success'}`}
              onClick={toggleAlarm}
              disabled={isProcessing}
            >
              <span className="btn-icon">{alarmEnabled ? "🔇" : "🔊"}</span>
              <span className="btn-text">{alarmEnabled ? "Mute Alarm" : "Enable Alarm"}</span>
              <span className="btn-shine"></span>
            </button>

            <button
              className={`btn ${borderEnabled ? 'btn-warning' : 'btn-secondary'}`}
              onClick={() => setBorderEnabled(prev => !prev)}
              disabled={isProcessing}
            >
              <span className="btn-icon">{borderEnabled ? "🟥" : "⬜"}</span>
              <span className="btn-text">{borderEnabled ? "Hide Border" : "Show Border"}</span>
              <span className="btn-shine"></span>
            </button>

          </div>

          {/* Processing Indicator */}
          {isProcessing && (
            <div className="processing-section">
              <div className="processing-indicator">
                <div className="processing-spinner">
                  <div className="spinner-ring"></div>
                  <div className="spinner-ring"></div>
                  <div className="spinner-ring"></div>
                </div>
                <div className="processing-text">
                  <span className="processing-title">Analyzing Video</span>
                  <span className="processing-subtitle">Waiting for analysis results...</span>
                </div>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill"></div>
              </div>
            </div>
          )}
        </div>

        {/* Video and Table Section */}
        {videoURL && (
          <div className="video-table-section">

            <div className="video-section card-3d">
              <div className="card-header">
                <span className="card-icon">🎬</span>
                <span className="card-title">Video Preview</span>
                {dataPoints.length > 0 && (
                  <span className="live-indicator">
                    <span className="live-dot"></span>
                    LIVE
                  </span>
                )}
              </div>
              <div className="video-wrapper">
                <video controls src={videoURL} />
              </div>
            </div>

            <div className="table-panel card-3d">
              <div className="card-header">
                <span className="card-icon">📊</span>
                <span className="card-title">Detection Log</span>
                <span className="data-count">{dataPoints.length} entries</span>
              </div>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>⏱️ Time</th>
                      <th>📈 Score</th>
                      <th>🔔 Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dataPoints.slice().reverse().map((row, index) => (
                      <tr key={index} className="table-row-animate">
                        <td>
                          <span className="time-badge">{row.time}s</span>
                        </td>
                        <td>
                          <span className="score-value">{row.score}</span>
                        </td>
                        <td>
                          <span className={`status-badge ${
                            row.alert
                              ? "status-alert"
                              : row.anomaly
                              ? "status-anomaly"
                              : "status-normal"
                          }`}>
                            {row.alert
                              ? "🚨 ALERT"
                              : row.anomaly
                              ? "⚠️ ANOMALY"
                              : "✅ NORMAL"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

        {/* Graph Section */}
        <div className="graph-section card-3d">
          <div className="card-header">
            <span className="card-icon">📈</span>
            <span className="card-title">Real-Time Analytics</span>
            {threshold !== null && (
              <span className="threshold-badge">
                Threshold: {threshold}
              </span>
            )}
          </div>

          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={dataPoints} margin={{ top: 20, right: 30, left: 20, bottom: 25 }}>
                <defs>
                  <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#059669" />
                    <stop offset="50%" stopColor="#10b981" />
                    <stop offset="100%" stopColor="#34d399" />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  dataKey="time" 
                  stroke="rgba(255,255,255,0.5)"
                  tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
                  label={{ 
                    value: 'Time (seconds)', 
                    position: 'insideBottom', 
                    offset: -15,
                    fill: '#d4af37',
                    fontSize: 14,
                    fontWeight: 600
                  }}
                />
                <YAxis 
                  stroke="rgba(255,255,255,0.5)"
                  tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
                  label={{ 
                    value: 'Anomaly Score', 
                    angle: -90, 
                    position: 'insideLeft',
                    fill: '#d4af37',
                    fontSize: 14,
                    fontWeight: 600
                  }}
                />
                <Tooltip 
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(16, 185, 129, 0.5)',
                    borderRadius: '12px',
                    boxShadow: '0 20px 40px rgba(0,0,0,0.4)'
                  }}
                  itemStyle={{ color: '#e2e8f0' }}
                  labelStyle={{ color: '#10b981' }}
                />
                {threshold !== null && (
                  <ReferenceLine
                    y={threshold}
                    stroke="#d4af37"
                    strokeDasharray="5 5"
                    strokeWidth={2}
                    label={{ 
                      value: "Threshold", 
                      fill: "#d4af37",
                      fontSize: 12,
                      fontWeight: 600
                    }}
                  />
                )}
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="url(#lineGradient)"
                  strokeWidth={3}
                  filter="url(#glow)"
                  dot={(props) => {
                    const { payload, cx, cy } = props;
                    if (payload.anomaly || payload.alert) {
                      return (
                        <g>
                          <circle cx={cx} cy={cy} r={8} fill="rgba(239, 68, 68, 0.3)" />
                          <circle cx={cx} cy={cy} r={5} fill="#ef4444" />
                        </g>
                      );
                    }
                    return (
                      <g>
                        <circle cx={cx} cy={cy} r={6} fill="rgba(16, 185, 129, 0.3)" />
                        <circle cx={cx} cy={cy} r={4} fill="#10b981" />
                      </g>
                    );
                  }}
                  activeDot={{ r: 8, fill: '#d4af37' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Stats Section */}
        {dataPoints.length > 0 && (
          <div className="stats-section">
            <div className="stat-card card-3d">
              <div className="stat-icon">📊</div>
              <div className="stat-value">{dataPoints.length}</div>
              <div className="stat-label">Total Points</div>
            </div>
            <div className="stat-card card-3d">
              <div className="stat-icon">⚠️</div>
              <div className="stat-value">{dataPoints.filter(d => d.anomaly).length}</div>
              <div className="stat-label">Anomalies</div>
            </div>
            <div className="stat-card card-3d">
              <div className="stat-icon">🚨</div>
              <div className="stat-value">{dataPoints.filter(d => d.alert).length}</div>
              <div className="stat-label">Alerts</div>
            </div>
            <div className="stat-card card-3d">
              <div className="stat-icon">✅</div>
              <div className="stat-value">
                {dataPoints.length > 0 
                  ? Math.round((dataPoints.filter(d => !d.anomaly && !d.alert).length / dataPoints.length) * 100)
                  : 0}%
              </div>
              <div className="stat-label">Normal Rate</div>
            </div>
          </div>
        )}

        {/* Export Section */}
        {dataPoints.length > 0 && !isProcessing && (
          <div className="export-section">
            <div className="export-card card-3d">
              <div className="export-content">
                <div className="export-left">
                  <span className="export-icon">📥</span>
                  <div className="export-info">
                    <span className="export-title">Export Analysis Report</span>
                    <span className="export-subtitle">
                      {dataPoints.length} data points • {dataPoints.filter(d => d.anomaly).length} anomalies detected
                    </span>
                  </div>
                </div>
                <button className="btn btn-export" onClick={exportCSV}>
                  <span className="btn-icon">📊</span>
                  <span className="btn-text">Export CSV</span>
                  <span className="btn-shine"></span>
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </>
  );
}

export default App;