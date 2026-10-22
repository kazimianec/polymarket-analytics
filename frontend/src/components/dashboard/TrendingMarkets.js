import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
const usdFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
});
export function TrendingMarkets({ markets }) {
    const top10 = markets.slice(0, 10);
    return (_jsx(Card, { sx: { mb: 4 }, children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "h6", gutterBottom: true, children: "Trending Markets" }), _jsx(Box, { sx: { overflowX: "auto" }, children: _jsxs(Table, { size: "small", children: [_jsx(TableHead, { children: _jsxs(TableRow, { children: [_jsx(TableCell, { children: "Question" }), _jsx(TableCell, { align: "right", children: "YES" }), _jsx(TableCell, { align: "right", children: "NO" }), _jsx(TableCell, { align: "right", children: "Volume" })] }) }), _jsx(TableBody, { children: top10.map((market) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: _jsx(Typography, { variant: "body2", sx: {
                                                    display: "-webkit-box",
                                                    WebkitLineClamp: 2,
                                                    WebkitBoxOrient: "vertical",
                                                    overflow: "hidden",
                                                    maxWidth: "400px",
                                                }, children: market.question }) }), _jsx(TableCell, { align: "right", children: _jsx(Chip, { label: `${(market.yes_price * 100).toFixed(1)}%`, size: "small", sx: {
                                                    backgroundColor: "success.light",
                                                    color: "success.dark",
                                                    fontWeight: 600,
                                                } }) }), _jsx(TableCell, { align: "right", children: _jsx(Chip, { label: `${(market.no_price * 100).toFixed(1)}%`, size: "small", sx: {
                                                    backgroundColor: "error.light",
                                                    color: "error.dark",
                                                    fontWeight: 600,
                                                } }) }), _jsx(TableCell, { align: "right", children: _jsx(Typography, { variant: "body2", children: usdFormatter.format(market.volume) }) })] }, market.id))) })] }) })] }) }));
}
