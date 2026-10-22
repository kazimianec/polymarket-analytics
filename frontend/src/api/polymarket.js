import { useQuery } from "@tanstack/react-query";
const API_BASE = "/api/v1";
async function fetchJson(url) {
    const res = await fetch(url);
    if (!res.ok)
        throw new Error(`HTTP ${res.status}`);
    return res.json();
}
// Stats Overview
export function useStatsOverview() {
    return useQuery({
        queryKey: ["polymarket", "stats", "overview"],
        queryFn: () => fetchJson(`${API_BASE}/stats/overview`),
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
}
// Trending Markets
export function useTrendingMarkets(limit = 20, offset = 0) {
    return useQuery({
        queryKey: ["polymarket", "markets", "trending", { limit, offset }],
        queryFn: () => fetchJson(`${API_BASE}/markets/trending?limit=${limit}&offset=${offset}`),
        staleTime: 60 * 1000, // 1 minute
    });
}
// Market Detail
export function useMarketDetail(marketId) {
    return useQuery({
        queryKey: ["polymarket", "markets", marketId],
        queryFn: () => fetchJson(`${API_BASE}/markets/${marketId}`),
        staleTime: 60 * 1000, // 1 minute
        enabled: !!marketId,
    });
}
// Market History
export function useMarketHistory(marketId, interval = "1d", fidelity = 50) {
    return useQuery({
        queryKey: ["polymarket", "markets", marketId, "history", { interval, fidelity }],
        queryFn: () => fetchJson(`${API_BASE}/markets/${marketId}/history?interval=${interval}&fidelity=${fidelity}`),
        staleTime: 60 * 1000, // 1 minute
        enabled: !!marketId,
    });
}
// Categories
export function useCategories() {
    return useQuery({
        queryKey: ["polymarket", "stats", "categories"],
        queryFn: () => fetchJson(`${API_BASE}/stats/categories`),
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
}
