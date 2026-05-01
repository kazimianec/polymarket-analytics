import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import type { MarketDetail } from "../../types/polymarket";

interface MarketInfoProps {
  market: MarketDetail;
}

const usdFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

function formatDate(dateString: string | null): string {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function MarketInfo({ market }: MarketInfoProps) {
  return (
    <Card sx={{ mb: 4 }}>
      <CardContent>
        <Typography variant="h5" component="h1" gutterBottom>
          {market.question}
        </Typography>

        {market.description && (
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            {market.description}
          </Typography>
        )}

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6}>
            <Box
              sx={{
                p: 2,
                backgroundColor: "success.light",
                borderRadius: 2,
                textAlign: "center",
              }}
            >
              <Typography variant="overline" color="success.dark">
                YES
              </Typography>
              <Typography
                variant="h3"
                color="success.dark"
                fontWeight={700}
              >
                {(market.yes_price * 100).toFixed(1)}%
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box
              sx={{
                p: 2,
                backgroundColor: "error.light",
                borderRadius: 2,
                textAlign: "center",
              }}
            >
              <Typography variant="overline" color="error.dark">
                NO
              </Typography>
              <Typography variant="h3" color="error.dark" fontWeight={700}>
                {(market.no_price * 100).toFixed(1)}%
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="body2" color="text.secondary">
              Volume
            </Typography>
            <Typography variant="body2" fontWeight={600}>
              {usdFormatter.format(market.volume)}
            </Typography>
          </Box>

          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="body2" color="text.secondary">
              Liquidity
            </Typography>
            <Typography variant="body2" fontWeight={600}>
              {usdFormatter.format(market.liquidity)}
            </Typography>
          </Box>

          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="body2" color="text.secondary">
              Category
            </Typography>
            <Typography variant="body2" fontWeight={600}>
              {market.category || "Uncategorized"}
            </Typography>
          </Box>

          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="body2" color="text.secondary">
              End Date
            </Typography>
            <Typography variant="body2" fontWeight={600}>
              {formatDate(market.end_date)}
            </Typography>
          </Box>
        </Box>

        {market.outcomes && market.outcomes.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Outcomes
            </Typography>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              {market.outcomes.map((outcome, index) => (
                <Chip
                  key={index}
                  label={outcome}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
}
