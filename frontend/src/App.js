import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Route, Routes } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import HealthPage from "./pages/system/HealthPage";
import MarketDetailPage from "./pages/MarketDetailPage";
export default function App() {
    return (_jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(DashboardPage, {}) }), _jsx(Route, { path: "/health", element: _jsx(HealthPage, {}) }), _jsx(Route, { path: "/markets/:marketId", element: _jsx(MarketDetailPage, {}) })] }));
}
