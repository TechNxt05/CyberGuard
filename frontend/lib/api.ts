import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface AnalysisRequest {
    message?: string;
    image_base64?: string;
    source?: string;
}

export interface IncidentRequest {
    description: string;
    user_context?: Record<string, string>;
}

export const checkScam = async (data: AnalysisRequest) => {
    const response = await api.post('/analyze-message', data);
    return response.data;
};

export const resolveIncident = async (data: IncidentRequest) => {
    const response = await api.post('/resolve-incident', data);
    return response.data;
};

export const solveDoubt = async (incidentId: string, question: string) => {
    const response = await api.post('/case/doubt', { incident_id: incidentId, question });
    return response.data;
};

export const assistForm = async (incidentId: string, actionItem: string) => {
    const response = await api.post('/case/form-assist', { incident_id: incidentId, action_item: actionItem });
    return response.data;
};
