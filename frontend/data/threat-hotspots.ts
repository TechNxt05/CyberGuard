// Districts widely reported in Indian news coverage as organised cyber-fraud hubs (the "Jamtara model"
// and the hotspots later flagged by I4C). Reference/illustrative only: no counts, not live data.

export interface ThreatHotspot {
  place: string;
  state: string;
  coordinates: [number, number]; // [longitude, latitude]
  knownFor: string;
}

export const INDIA_FRAUD_HUBS: ThreatHotspot[] = [
  { place: "Jamtara", state: "Jharkhand", coordinates: [86.8028, 23.9598], knownFor: "Vishing / OTP & KYC fraud" },
  { place: "Deoghar", state: "Jharkhand", coordinates: [86.6950, 24.4850], knownFor: "Vishing / OTP fraud" },
  { place: "Nuh (Mewat)", state: "Haryana", coordinates: [77.0050, 28.1050], knownFor: "Marketplace (OLX) and sextortion fraud" },
  { place: "Bharatpur", state: "Rajasthan", coordinates: [77.4895, 27.2152], knownFor: "Marketplace and sextortion fraud" },
  { place: "Mathura", state: "Uttar Pradesh", coordinates: [77.6737, 27.4924], knownFor: "Marketplace and sextortion fraud" },
];
