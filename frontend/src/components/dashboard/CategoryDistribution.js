import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, } from "recharts";
const usdFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
});
export function CategoryDistribution({ categories }) {
    const top8 = categories.slice(0, 8);
    const chartData = top8.map((cat) => ({
        name: cat.label,
        volume: cat.volume,
    }));
    return (_jsx(Card, { children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "h6", gutterBottom: true, children: "Category Distribution" }), _jsx(Box, { sx: { width: "100%", height: 300 }, children: _jsx(ResponsiveContainer, { children: _jsxs(BarChart, { data: chartData, layout: "vertical", margin: { top: 5, right: 30, left: 100, bottom: 5 }, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3" }), _jsx(XAxis, { type: "number", tickFormatter: (value) => usdFormatter.format(value) }), _jsx(YAxis, { type: "category", dataKey: "name", width: 90, tick: { fontSize: 12 } }), _jsx(Tooltip, { formatter: (value) => [usdFormatter.format(value), "Volume"] }), _jsx(Bar, { dataKey: "volume", fill: "#1976d2", radius: [0, 4, 4, 0] })] }) }) })] }) }));
}
