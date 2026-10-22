import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
const usdFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
});
export function StatsOverview({ data }) {
    const topCategory = data.top_categories[0];
    return (_jsxs(Grid, { container: true, spacing: 3, sx: { mb: 4 }, children: [_jsx(Grid, { xs: 12, sm: 4, children: _jsx(Card, { children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "body2", color: "text.secondary", gutterBottom: true, children: "Total Active Markets" }), _jsx(Typography, { variant: "h3", children: data.total_active_markets.toLocaleString() })] }) }) }), _jsx(Grid, { xs: 12, sm: 4, children: _jsx(Card, { children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "body2", color: "text.secondary", gutterBottom: true, children: "Total Volume" }), _jsx(Typography, { variant: "h3", children: usdFormatter.format(data.total_volume) })] }) }) }), _jsx(Grid, { xs: 12, sm: 4, children: _jsx(Card, { children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "body2", color: "text.secondary", gutterBottom: true, children: "Top Category" }), _jsx(Typography, { variant: "h5", gutterBottom: true, children: topCategory?.label ?? "N/A" }), _jsx(Typography, { variant: "body2", color: "text.secondary", children: topCategory ? usdFormatter.format(topCategory.volume) : "" })] }) }) })] }));
}
