import React from 'react';
import type { TimelineEvent } from '../types';

interface EventTimelineProps {
    events: TimelineEvent[];
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
    return (
        <section className="events-section">
            <h2>Live Event Timeline</h2>
            <div className="events-timeline" id="events-timeline">
                {events.map((event) => (
                    <div key={event.id} className="event-item" style={{ marginBottom: '15px' }}>
                        <div style={{ fontSize: '12px', color: '#888', fontFamily: "'JetBrains Mono', monospace" }}>
                            {event.time}
                        </div>
                        <div style={{ fontWeight: 600, marginTop: '4px', color: '#fff' }}>
                            {event.message}
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
};
