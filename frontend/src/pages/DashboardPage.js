import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { useStatsOverview } from "../api/polymarket";
import { CategoryDistribution } from "../components/dashboard/CategoryDistribution";
import { StatsOverview } from "../components/dashboard/StatsOverview";
import { TrendingMarkets } from "../components/dashboard/TrendingMarkets";
function DashboardSkeleton() {
    return (_jsxs(Container, { maxWidth: "lg", sx: { py: 4 }, children: [_jsx(Skeleton, { variant: "text", width: 300, height: 40, sx: { mb: 2 } }), _jsx(Skeleton, { variant: "text", width: 200, height: 24, sx: { mb: 4 } }), _jsxs(Box, { sx: { display: "flex", gap: 3, mb: 4 }, children: [_jsx(Skeleton, { variant: "rounded", width: "100%", height: 120 }), _jsx(Skeleton, { variant: "rounded", width: "100%", height: 120 }), _jsx(Skeleton, { variant: "rounded", width: "100%", height: 120 })] }), _jsx(Skeleton, { variant: "rounded", width: "100%", height: 400, sx: { mb: 4 } }), _jsx(Skeleton, { variant: "rounded", width: "100%", height: 350 })] }));
}
export default function DashboardPage() {
    const { data, isLoading, error } = useStatsOverview();
    if (isLoading) {
        return _jsx(DashboardSkeleton, {});
    }
    if (error) {
        return (_jsx(Container, { maxWidth: "lg", sx: { py: 4 }, children: _jsxs(Alert, { severity: "error", children: ["Failed to load stats: ", error.message] }) }));
    }
    if (!data) {
        return (_jsx(Container, { maxWidth: "lg", sx: { py: 4 }, children: _jsx(Alert, { severity: "warning", children: "No data available" }) }));
    }
    return (_jsxs(Container, { maxWidth: "lg", sx: { py: 4 }, children: [_jsx(Typography, { variant: "h4", gutterBottom: true, children: "Polymarket Analytics" }), _jsx(Typography, { variant: "body1", color: "text.secondary", sx: { mb: 4 }, children: "Prediction market insights" }), _jsx(StatsOverview, { data: data }), _jsx(TrendingMarkets, { markets: data.trending_markets }), _jsx(CategoryDistribution, { categories: data.top_categories })] }));
}
