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
import type { TrendingMarketSummary } from "../../types/polymarket";

const usdFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

interface TrendingMarketsProps {
  markets: TrendingMarketSummary[];
}

export function TrendingMarkets({ markets }: TrendingMarketsProps) {
  const top10 = markets.slice(0, 10);

  return (
    <Card sx={{ mb: 4 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Trending Markets
        </Typography>
        <Box sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Question</TableCell>
                <TableCell align="right">YES</TableCell>
                <TableCell align="right">NO</TableCell>
                <TableCell align="right">Volume</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {top10.map((market) => (
                <TableRow key={market.id}>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                        maxWidth: "400px",
                      }}
                    >
                      {market.question}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={`${(market.yes_price * 100).toFixed(1)}%`}
                      size="small"
                      sx={{
                        backgroundColor: "success.light",
                        color: "success.dark",
                        fontWeight: 600,
                      }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={`${(market.no_price * 100).toFixed(1)}%`}
                      size="small"
                      sx={{
                        backgroundColor: "error.light",
                        color: "error.dark",
                        fontWeight: 600,
                      }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {usdFormatter.format(market.volume)}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </CardContent>
    </Card>
  );
}
