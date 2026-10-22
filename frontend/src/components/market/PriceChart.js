import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, } from "recharts";
function formatPercentage(value) {
    return `${(value * 100).toFixed(0)}%`;
}
function formatXAxis(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
    });
}
function CustomTooltip({ active, payload, label }) {
    if (active && payload && payload.length) {
        const date = new Date(label * 1000);
        return (_jsxs(Box, { sx: {
                backgroundColor: "background.paper",
                border: 1,
                borderColor: "divider",
                borderRadius: 1,
                p: 1,
            }, children: [_jsx(Typography, { variant: "body2", children: date.toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                    }) }), _jsx(Typography, { variant: "body2", color: "primary.main", fontWeight: 600, children: formatPercentage(payload[0].value) })] }));
    }
    return null;
}
export function PriceChart({ history }) {
    if (history.length === 0) {
        return (_jsx(Card, { sx: { mb: 4 }, children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "h6", gutterBottom: true, children: "Price History" }), _jsx(Box, { sx: {
                            height: 300,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }, children: _jsx(Typography, { color: "text.secondary", children: "No price history available" }) })] }) }));
    }
    return (_jsx(Card, { sx: { mb: 4 }, children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "h6", gutterBottom: true, children: "Price History" }), _jsx(Box, { sx: { height: 300, width: "100%" }, children: _jsx(ResponsiveContainer, { children: _jsxs(LineChart, { data: history, margin: { top: 5, right: 20, left: 10, bottom: 5 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3" }), _jsx(XAxis, { dataKey: "timestamp", tickFormatter: formatXAxis, stroke: "text.secondary", fontSize: 12 }), _jsx(YAxis, { domain: [0, 1], tickFormatter: formatPercentage, stroke: "text.secondary", fontSize: 12, tickCount: 6 }), _jsx(Tooltip, { content: _jsx(CustomTooltip, {}) }), _jsx(Line, { type: "monotone", dataKey: "price", stroke: "#1976d2", strokeWidth: 2, dot: false, activeDot: { r: 4 } })] }) }) })] }) }));
}
