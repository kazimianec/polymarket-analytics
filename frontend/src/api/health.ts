import { useQuery } from "@tanstack/react-query";

export interface CheckResult {
  status: "ok" | "error";
  detail: string | null;
}

export interface HealthStatus {
  status: "ok" | "degraded";
  app_name: string;
  env: string;
  runtime: "container" | "local";
  checks: Record<string, CheckResult>;
}

async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch("/api/v1/health");
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json() as Promise<HealthStatus>;
}

export function useHealthCheck() {
  return useQuery<HealthStatus, Error>({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 1,
  });
}
