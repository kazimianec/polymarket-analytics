import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import { Link, useParams } from "react-router-dom";
import { ArrowBack } from "@mui/icons-material";
import { useMarketDetail, useMarketHistory } from "../api/polymarket";
import { MarketInfo } from "../components/market/MarketInfo";
import { PriceChart } from "../components/market/PriceChart";

function MarketDetailSkeleton() {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Skeleton variant="text" width={200} height={40} sx={{ mb: 2 }} />
      <Skeleton variant="rounded" width="100%" height={300} sx={{ mb: 4 }} />
      <Skeleton variant="rounded" width="100%" height={400} />
    </Container>
  );
}

export default function MarketDetailPage() {
  const { marketId } = useParams<{ marketId: string }>();

  const {
    data: market,
    isLoading: isLoadingMarket,
    error: marketError,
  } = useMarketDetail(marketId!);

  const {
    data: history,
    isLoading: isLoadingHistory,
  } = useMarketHistory(marketId!);

  if (isLoadingMarket) {
    return <MarketDetailSkeleton />;
  }

  if (marketError) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          component={Link}
          to="/"
          sx={{ mb: 2 }}
        >
          Back
        </Button>
        <Alert severity="error">
          Failed to load market: {marketError.message}
        </Alert>
      </Container>
    );
  }

  if (!market) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          component={Link}
          to="/"
          sx={{ mb: 2 }}
        >
          Back
        </Button>
        <Alert severity="warning">Market not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBack />}
        component={Link}
        to="/"
        sx={{ mb: 2 }}
      >
        Back
      </Button>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Market ID: {marketId}
      </Typography>

      <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <MarketInfo market={market} />
        {isLoadingHistory ? (
          <Skeleton variant="rounded" width="100%" height={300} />
        ) : (
          <PriceChart history={history?.history || []} />
        )}
      </Box>
    </Container>
  );
}
