import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useHealthCheck } from "../../api/health";
function CheckRow({ name, check }) {
    return (_jsxs(Stack, { direction: "row", justifyContent: "space-between", alignItems: "center", sx: { py: 0.5 }, children: [_jsx(Typography, { variant: "body2", children: name }), _jsxs(Stack, { alignItems: "flex-end", children: [_jsx(Chip, { label: check.status, color: check.status === "ok" ? "success" : "error", size: "small" }), check.detail && (_jsx(Typography, { variant: "caption", color: "text.secondary", children: check.detail }))] })] }));
}
export default function HealthPage() {
    const { data, isLoading, isError } = useHealthCheck();
    return (_jsxs(Box, { sx: {
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100vh",
            gap: 2,
        }, children: [_jsx(Typography, { variant: "overline", color: "text.secondary", children: "System Status" }), _jsx(Typography, { variant: "h5", children: data ? data.app_name : "API Health Check" }), isLoading && _jsx(CircularProgress, { size: 24 }), isError && (_jsx(Chip, { label: "error", color: "error", "data-testid": "health-status" })), data && (_jsxs(Stack, { direction: "row", gap: 1, alignItems: "center", children: [_jsx(Chip, { label: data.env, variant: "outlined", size: "small", "data-testid": "health-env" }), _jsx(Chip, { label: data.runtime, variant: "outlined", size: "small", "data-testid": "health-runtime" }), _jsx(Chip, { label: data.status, color: data.status === "ok" ? "success" : "warning", "data-testid": "health-status" })] })), data && (_jsxs(_Fragment, { children: [_jsx(Divider, { sx: { width: "100%", maxWidth: 400 } }), _jsx(Stack, { sx: { width: "100%", maxWidth: 400 }, "data-testid": "health-checks", children: Object.entries(data.checks).map(([name, check]) => (_jsx(CheckRow, { name: name, check: check }, name))) })] }))] }));
}
