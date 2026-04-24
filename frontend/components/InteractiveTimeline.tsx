import React from "react";
import { Clock } from "lucide-react";

interface TimelineEvent {
  time: str;
  description: str;
}

interface InteractiveTimelineProps {
  events: TimelineEvent[];
}

export function InteractiveTimeline({ events }: InteractiveTimelineProps) {
  if (!events || events.length === 0) {
    return <div className="text-gray-500 text-sm italic">No events in timeline yet.</div>;
  }

  return (
    <div className="relative border-l border-blue-500/30 ml-3 space-y-6 py-2">
      {events.map((event, index) => (
        <div key={index} className="relative pl-6 group">
          <div className="absolute w-3 h-3 bg-blue-500 rounded-full -left-[6.5px] top-1 group-hover:shadow-[0_0_10px_rgba(59,130,246,0.8)] transition-shadow" />
          <div className="flex flex-col">
            <span className="text-xs text-blue-400 font-mono mb-1 flex items-center gap-1">
              <Clock size={12} /> {event.time}
            </span>
            <span className="text-sm text-gray-200">{event.description}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
