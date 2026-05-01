import { Route, Routes } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import HealthPage from "./pages/system/HealthPage";
import MarketDetailPage from "./pages/MarketDetailPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/health" element={<HealthPage />} />
      <Route path="/markets/:marketId" element={<MarketDetailPage />} />
    </Routes>
  );
}
