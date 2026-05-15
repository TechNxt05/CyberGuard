"use client";

import React, { useState } from 'react';
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from 'react-simple-maps';
import { INDIA_THREAT_HOTSPOTS, ThreatHotspot } from '@/data/threat-hotspots';

// India GeoJSON URL (use topojson CDN)
const INDIA_TOPO_URL = "https://raw.githubusercontent.com/deldersveld/topojson/master/countries/india/india-states.json";

const ThreatMap = () => {
  const [tooltip, setTooltip] = useState<ThreatHotspot | null>(null);
  
  // Scale bubble size by threat count
  const getRadius = (count: number) => Math.max(4, Math.min(20, count / 200));
  
  // Color by severity
  const getSeverityColor = (severity: string) => {
    switch(severity) {
        case 'CRITICAL': return '#ef4444';
        case 'HIGH': return '#f97316';
        case 'MEDIUM': return '#eab308';
        case 'LOW': return '#22c55e';
        default: return '#6b7280';
    }
  };

  const totalReports = INDIA_THREAT_HOTSPOTS.reduce((sum, h) => sum + h.threatCount, 0);

  return (
    <div className="relative w-full bg-black/40 rounded-2xl border border-white/5 p-4 glass-panel mt-4">
      <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2">
        <h3 className="text-sm font-semibold text-white tracking-widest uppercase text-[10px]">🗺️ Geospatial Threat Intelligence</h3>
        <span className="text-xs text-gray-400 font-mono">India · {totalReports.toLocaleString()} reports today</span>
      </div>
      
      <div className="relative w-full h-[400px] bg-slate-950/50 rounded-xl overflow-hidden hidden sm:block">
          <ComposableMap
            projection="geoMercator"
            projectionConfig={{ scale: 1000, center: [82, 23] }}
            style={{ width: '100%', height: '100%', background: 'transparent' }}
          >
            <ZoomableGroup>
              <Geographies geography={INDIA_TOPO_URL}>
                {({ geographies }) =>
                  geographies.map(geo => (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill="#1f2937"
                      stroke="#374151"
                      strokeWidth={0.5}
                      style={{
                        default: { outline: 'none' },
                        hover: { fill: '#374151', outline: 'none' },
                        pressed: { fill: '#374151', outline: 'none' }
                      }}
                    />
                  ))
                }
              </Geographies>
              
              {INDIA_THREAT_HOTSPOTS.map(hotspot => (
                <Marker
                  key={hotspot.city}
                  coordinates={hotspot.coordinates}
                  onMouseEnter={() => setTooltip(hotspot)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {/* Pulsing outer ring */}
                  <circle
                    r={getRadius(hotspot.threatCount) + 4}
                    fill={getSeverityColor(hotspot.severity)}
                    fillOpacity={0.15}
                    className="animate-ping"
                  />
                  {/* Solid inner dot */}
                  <circle
                    r={getRadius(hotspot.threatCount)}
                    fill={getSeverityColor(hotspot.severity)}
                    fillOpacity={0.85}
                    stroke="#fff"
                    strokeWidth={0.5}
                    style={{ cursor: 'pointer' }}
                  />
                </Marker>
              ))}
            </ZoomableGroup>
          </ComposableMap>
          
          {/* Tooltip */}
          {tooltip && (
            <div className="absolute top-4 left-4 bg-black/80 border border-white/10 rounded-lg p-3 z-10 max-w-48 backdrop-blur-md">
              <p className="text-white font-bold text-sm tracking-wide">{tooltip.city}</p>
              <p className="text-gray-400 text-xs">{tooltip.state}</p>
              <p className="text-red-400 text-[10px] font-mono mt-1">{tooltip.threatCount.toLocaleString()} reports</p>
              <p className="text-gray-300 text-xs font-medium uppercase tracking-tighter mt-1">{tooltip.primaryThreatType}</p>
            </div>
          )}
      </div>

      <div className="sm:hidden flex items-center justify-center h-24 bg-white/5 rounded-xl border border-white/5">
          <p className="text-xs text-gray-400 text-center px-4">View on desktop to interact with the full Geospatial Threat Map.</p>
      </div>
      
      {/* Legend */}
      <div className="flex items-center gap-4 mt-4 flex-wrap pb-1">
        {['CRITICAL', 'HIGH', 'MEDIUM'].map(sev => (
          <div key={sev} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ background: getSeverityColor(sev) }} />
            <span className="text-[10px] uppercase font-bold tracking-widest text-gray-400">{sev}</span>
          </div>
        ))}
        <span className="text-[10px] text-gray-500 ml-auto hidden sm:inline">Bubble size = report volume</span>
      </div>
    </div>
  );
};

export default ThreatMap;
