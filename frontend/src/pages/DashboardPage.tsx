import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { useStatsOverview } from "../api/polymarket";
import { CategoryDistribution } from "../components/dashboard/CategoryDistribution";
import { StatsOverview } from "../components/dashboard/StatsOverview";
import { TrendingMarkets } from "../components/dashboard/TrendingMarkets";

function DashboardSkeleton() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Skeleton variant="text" width={300} height={40} sx={{ mb: 2 }} />
      <Skeleton variant="text" width={200} height={24} sx={{ mb: 4 }} />

      <Box sx={{ display: "flex", gap: 3, mb: 4 }}>
        <Skeleton variant="rounded" width="100%" height={120} />
        <Skeleton variant="rounded" width="100%" height={120} />
        <Skeleton variant="rounded" width="100%" height={120} />
      </Box>

      <Skeleton variant="rounded" width="100%" height={400} sx={{ mb: 4 }} />
      <Skeleton variant="rounded" width="100%" height={350} />
    </Container>
  );
}

export default function DashboardPage() {
  const { data, isLoading, error } = useStatsOverview();

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">Failed to load stats: {error.message}</Alert>
      </Container>
    );
  }

  if (!data) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">No data available</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Polymarket Analytics
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Prediction market insights
      </Typography>

      <StatsOverview data={data} />
      <TrendingMarkets markets={data.trending_markets} />
      <CategoryDistribution categories={data.top_categories} />
    </Container>
  );
}
