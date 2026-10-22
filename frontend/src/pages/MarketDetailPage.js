import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { Link, useParams } from "react-router-dom";
import { ArrowBack } from "@mui/icons-material";
import { useMarketDetail, useMarketHistory } from "../api/polymarket";
import { MarketInfo } from "../components/market/MarketInfo";
import { PriceChart } from "../components/market/PriceChart";
function MarketDetailSkeleton() {
    return (_jsxs(Container, { maxWidth: "md", sx: { py: 4 }, children: [_jsx(Skeleton, { variant: "text", width: 200, height: 40, sx: { mb: 2 } }), _jsx(Skeleton, { variant: "rounded", width: "100%", height: 300, sx: { mb: 4 } }), _jsx(Skeleton, { variant: "rounded", width: "100%", height: 400 })] }));
}
export default function MarketDetailPage() {
    const { marketId } = useParams();
    const { data: market, isLoading: isLoadingMarket, error: marketError, } = useMarketDetail(marketId);
    const { data: history, isLoading: isLoadingHistory, } = useMarketHistory(marketId);
    if (isLoadingMarket) {
        return _jsx(MarketDetailSkeleton, {});
    }
    if (marketError) {
        return (_jsxs(Container, { maxWidth: "md", sx: { py: 4 }, children: [_jsx(Button, { startIcon: _jsx(ArrowBack, {}), component: Link, to: "/", sx: { mb: 2 }, children: "Back" }), _jsxs(Alert, { severity: "error", children: ["Failed to load market: ", marketError.message] })] }));
    }
    if (!market) {
        return (_jsxs(Container, { maxWidth: "md", sx: { py: 4 }, children: [_jsx(Button, { startIcon: _jsx(ArrowBack, {}), component: Link, to: "/", sx: { mb: 2 }, children: "Back" }), _jsx(Alert, { severity: "warning", children: "Market not found" })] }));
    }
    return (_jsxs(Container, { maxWidth: "md", sx: { py: 4 }, children: [_jsx(Button, { startIcon: _jsx(ArrowBack, {}), component: Link, to: "/", sx: { mb: 2 }, children: "Back" }), _jsxs(Typography, { variant: "body2", color: "text.secondary", sx: { mb: 2 }, children: ["Market ID: ", marketId] }), _jsxs(Box, { sx: { display: "flex", flexDirection: "column", gap: 4 }, children: [_jsx(MarketInfo, { market: market }), isLoadingHistory ? (_jsx(Skeleton, { variant: "rounded", width: "100%", height: 300 })) : (_jsx(PriceChart, { history: history?.history || [] }))] })] }));
}
