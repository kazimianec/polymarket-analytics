import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import type { StatsOverview } from "../../types/polymarket";

const usdFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

interface StatsOverviewProps {
  data: StatsOverview;
}

export function StatsOverview({ data }: StatsOverviewProps) {
  const topCategory = data.top_categories[0];

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid xs={12} sm={4}>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Total Active Markets
            </Typography>
            <Typography variant="h3">
              {data.total_active_markets.toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid xs={12} sm={4}>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Total Volume
            </Typography>
            <Typography variant="h3">
              {usdFormatter.format(data.total_volume)}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid xs={12} sm={4}>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Top Category
            </Typography>
            <Typography variant="h5" gutterBottom>
              {topCategory?.label ?? "N/A"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {topCategory ? usdFormatter.format(topCategory.volume) : ""}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
