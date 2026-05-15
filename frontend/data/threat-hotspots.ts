export interface ThreatHotspot {
  city: string;
  state: string;
  coordinates: [number, number]; // [longitude, latitude]
  threatCount: number;
  primaryThreatType: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export const INDIA_THREAT_HOTSPOTS: ThreatHotspot[] = [
  { city: "Mumbai", state: "Maharashtra", coordinates: [72.8777, 19.0760], threatCount: 4821, primaryThreatType: "UPI Fraud", severity: "CRITICAL" },
  { city: "Delhi", state: "Delhi", coordinates: [77.1025, 28.7041], threatCount: 3947, primaryThreatType: "Phishing", severity: "CRITICAL" },
  { city: "Bangalore", state: "Karnataka", coordinates: [77.5946, 12.9716], threatCount: 2834, primaryThreatType: "Investment Fraud", severity: "HIGH" },
  { city: "Hyderabad", state: "Telangana", coordinates: [78.4867, 17.3850], threatCount: 1923, primaryThreatType: "Vishing", severity: "HIGH" },
  { city: "Ahmedabad", state: "Gujarat", coordinates: [72.5714, 23.0225], threatCount: 1654, primaryThreatType: "UPI Fraud", severity: "HIGH" },
  { city: "Chennai", state: "Tamil Nadu", coordinates: [80.2707, 13.0827], threatCount: 1432, primaryThreatType: "Phishing", severity: "HIGH" },
  { city: "Kolkata", state: "West Bengal", coordinates: [88.3639, 22.5726], threatCount: 1287, primaryThreatType: "Courier Fraud", severity: "MEDIUM" },
  { city: "Pune", state: "Maharashtra", coordinates: [73.8567, 18.5204], threatCount: 1156, primaryThreatType: "Investment Fraud", severity: "MEDIUM" },
  { city: "Jaipur", state: "Rajasthan", coordinates: [75.7873, 26.9124], threatCount: 987, primaryThreatType: "Sextortion", severity: "MEDIUM" },
  { city: "Lucknow", state: "Uttar Pradesh", coordinates: [80.9462, 26.8467], threatCount: 876, primaryThreatType: "Vishing", severity: "MEDIUM" },
  { city: "Surat", state: "Gujarat", coordinates: [72.8311, 21.1702], threatCount: 743, primaryThreatType: "UPI Fraud", severity: "MEDIUM" },
  { city: "Noida", state: "UP", coordinates: [77.3910, 28.5355], threatCount: 698, primaryThreatType: "Tech Support Fraud", severity: "MEDIUM" },
  { city: "Jamtara", state: "Jharkhand", coordinates: [86.8028, 23.9598], threatCount: 542, primaryThreatType: "Vishing (Origin Hub)", severity: "HIGH" },
  { city: "Mewat", state: "Haryana", coordinates: [77.0151, 28.0000], threatCount: 489, primaryThreatType: "OLX/Social Fraud", severity: "HIGH" },
];
