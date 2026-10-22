import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
export default function HomePage() {
    return (_jsxs(Box, { sx: {
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100vh",
            gap: 2,
        }, children: [_jsx(Typography, { variant: "h4", children: "Welcome" }), _jsx(Typography, { variant: "body1", color: "text.secondary", children: "Replace this page with your app." })] }));
}
