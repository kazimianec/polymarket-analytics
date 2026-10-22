import { useQuery } from "@tanstack/react-query";
async function fetchHealth() {
    const response = await fetch("/api/v1/health");
    if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
}
export function useHealthCheck() {
    return useQuery({
        queryKey: ["health"],
        queryFn: fetchHealth,
        retry: 1,
    });
}
