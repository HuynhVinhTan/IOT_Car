import { apiRequest } from "./apiClient";

const API_BASE = "/api/maps";

export interface MapNode {
  id: string;
  x: number;
  y: number;
  label?: string;
  type: "normal" | "home" | "target" | "checkpoint";
}

export interface MapEdge {
  id: string;
  from: string;
  to: string;
  distance?: number;
  bidirectional?: boolean;
}

export interface Map {
  id: string;
  name?: string;
  nodes: MapNode[];
  edges: MapEdge[];
}

export async function listMaps(): Promise<Map[]> {
  return apiRequest<Map[]>(API_BASE);
}

export async function getMap(mapId: string): Promise<Map> {
  return apiRequest<Map>(`${API_BASE}/${mapId}`);
}

export async function saveMap(map: Map): Promise<{ ok: boolean; id: string }> {
  return apiRequest<{ ok: boolean; id: string }>(API_BASE, {
    method: "POST",
    body: JSON.stringify(map),
  });
}

export async function activateMap(mapId: string): Promise<{ ok: boolean }> {
  return apiRequest<{ ok: boolean }>(`${API_BASE}/${mapId}/activate`, {
    method: "POST",
  });
}

export async function getActiveMap(): Promise<Map> {
  return apiRequest<Map>(`${API_BASE}/active`);
}
