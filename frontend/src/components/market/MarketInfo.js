import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
const usdFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
});
function formatDate(dateString) {
    if (!dateString)
        return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
    });
}
export function MarketInfo({ market }) {
    return (_jsx(Card, { sx: { mb: 4 }, children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "h5", component: "h1", gutterBottom: true, children: market.question }), market.description && (_jsx(Typography, { variant: "body1", color: "text.secondary", sx: { mb: 2 }, children: market.description })), _jsxs(Grid, { container: true, spacing: 2, sx: { mb: 3 }, children: [_jsx(Grid, { item: true, xs: 6, children: _jsxs(Box, { sx: {
                                    p: 2,
                                    backgroundColor: "success.light",
                                    borderRadius: 2,
                                    textAlign: "center",
                                }, children: [_jsx(Typography, { variant: "overline", color: "success.dark", children: "YES" }), _jsxs(Typography, { variant: "h3", color: "success.dark", fontWeight: 700, children: [(market.yes_price * 100).toFixed(1), "%"] })] }) }), _jsx(Grid, { item: true, xs: 6, children: _jsxs(Box, { sx: {
                                    p: 2,
                                    backgroundColor: "error.light",
                                    borderRadius: 2,
                                    textAlign: "center",
                                }, children: [_jsx(Typography, { variant: "overline", color: "error.dark", children: "NO" }), _jsxs(Typography, { variant: "h3", color: "error.dark", fontWeight: 700, children: [(market.no_price * 100).toFixed(1), "%"] })] }) })] }), _jsx(Divider, { sx: { mb: 2 } }), _jsxs(Box, { sx: { display: "flex", flexDirection: "column", gap: 1 }, children: [_jsxs(Box, { sx: { display: "flex", justifyContent: "space-between" }, children: [_jsx(Typography, { variant: "body2", color: "text.secondary", children: "Volume" }), _jsx(Typography, { variant: "body2", fontWeight: 600, children: usdFormatter.format(market.volume) })] }), _jsxs(Box, { sx: { display: "flex", justifyContent: "space-between" }, children: [_jsx(Typography, { variant: "body2", color: "text.secondary", children: "Liquidity" }), _jsx(Typography, { variant: "body2", fontWeight: 600, children: usdFormatter.format(market.liquidity) })] }), _jsxs(Box, { sx: { display: "flex", justifyContent: "space-between" }, children: [_jsx(Typography, { variant: "body2", color: "text.secondary", children: "Category" }), _jsx(Typography, { variant: "body2", fontWeight: 600, children: market.category || "Uncategorized" })] }), _jsxs(Box, { sx: { display: "flex", justifyContent: "space-between" }, children: [_jsx(Typography, { variant: "body2", color: "text.secondary", children: "End Date" }), _jsx(Typography, { variant: "body2", fontWeight: 600, children: formatDate(market.end_date) })] })] }), market.outcomes && market.outcomes.length > 0 && (_jsxs(_Fragment, { children: [_jsx(Divider, { sx: { my: 2 } }), _jsx(Typography, { variant: "body2", color: "text.secondary", sx: { mb: 1 }, children: "Outcomes" }), _jsx(Box, { sx: { display: "flex", gap: 1, flexWrap: "wrap" }, children: market.outcomes.map((outcome, index) => (_jsx(Chip, { label: outcome, size: "small", variant: "outlined" }, index))) })] }))] }) }));
}
