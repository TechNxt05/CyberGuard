"use client";

import React, { useState } from 'react';
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from 'react-simple-maps';
import { INDIA_FRAUD_HUBS, ThreatHotspot } from '@/data/threat-hotspots';

const INDIA_TOPO_URL = "https://raw.githubusercontent.com/deldersveld/topojson/master/countries/india/india-states.json";

const ThreatMap = () => {
  const [tooltip, setTooltip] = useState<ThreatHotspot | null>(null);

  return (
    <div className="relative w-full bg-black/40 rounded-2xl border border-white/5 p-4 glass-panel mt-4">
      <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2 gap-2">
        <h3 className="font-semibold text-white tracking-widest uppercase text-[10px]">Known Cyber-Fraud Hubs</h3>
        <span className="text-[10px] text-gray-500">Reference only · from public news reporting</span>
      </div>

      <div className="relative w-full h-[400px] bg-slate-950/50 rounded-xl overflow-hidden hidden sm:block">
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{ scale: 1000, center: [82, 23] }}
          style={{ width: '100%', height: '100%', background: 'transparent' }}
        >
          <ZoomableGroup>
            <Geographies geography={INDIA_TOPO_URL}>
              {({ geographies }: { geographies: { rsmKey: string }[] }) =>
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

            {INDIA_FRAUD_HUBS.map(hub => (
              <Marker
                key={hub.place}
                coordinates={hub.coordinates}
                onMouseEnter={() => setTooltip(hub)}
                onMouseLeave={() => setTooltip(null)}
              >
                <circle r={7} fill="#f97316" fillOpacity={0.85} stroke="#fff" strokeWidth={0.5} style={{ cursor: 'pointer' }} />
              </Marker>
            ))}
          </ZoomableGroup>
        </ComposableMap>

        {tooltip && (
          <div className="absolute top-4 left-4 bg-black/80 border border-white/10 rounded-lg p-3 z-10 max-w-56 backdrop-blur-md">
            <p className="text-white font-bold text-sm tracking-wide">{tooltip.place}</p>
            <p className="text-gray-400 text-xs">{tooltip.state}</p>
            <p className="text-gray-300 text-xs mt-1">{tooltip.knownFor}</p>
          </div>
        )}
      </div>

      <div className="sm:hidden space-y-1">
        {INDIA_FRAUD_HUBS.map(hub => (
          <p key={hub.place} className="text-xs text-gray-400"><span className="text-white">{hub.place}</span>, {hub.state} — {hub.knownFor}</p>
        ))}
      </div>
    </div>
  );
};

export default ThreatMap;
