import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useHealthCheck } from "../../api/health";
import type { CheckResult } from "../../api/health";

function CheckRow({ name, check }: { name: string; check: CheckResult }) {
  return (
    <Stack
      direction="row"
      justifyContent="space-between"
      alignItems="center"
      sx={{ py: 0.5 }}
    >
      <Typography variant="body2">{name}</Typography>
      <Stack alignItems="flex-end">
        <Chip
          label={check.status}
          color={check.status === "ok" ? "success" : "error"}
          size="small"
        />
        {check.detail && (
          <Typography variant="caption" color="text.secondary">
            {check.detail}
          </Typography>
        )}
      </Stack>
    </Stack>
  );
}

export default function HealthPage() {
  const { data, isLoading, isError } = useHealthCheck();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        gap: 2,
      }}
    >
      <Typography variant="overline" color="text.secondary">
        System Status
      </Typography>

      <Typography variant="h5">
        {data ? data.app_name : "API Health Check"}
      </Typography>

      {isLoading && <CircularProgress size={24} />}

      {isError && (
        <Chip label="error" color="error" data-testid="health-status" />
      )}

      {data && (
        <Stack direction="row" gap={1} alignItems="center">
          <Chip
            label={data.env}
            variant="outlined"
            size="small"
            data-testid="health-env"
          />
          <Chip
            label={data.runtime}
            variant="outlined"
            size="small"
            data-testid="health-runtime"
          />
          <Chip
            label={data.status}
            color={data.status === "ok" ? "success" : "warning"}
            data-testid="health-status"
          />
        </Stack>
      )}

      {data && (
        <>
          <Divider sx={{ width: "100%", maxWidth: 400 }} />
          <Stack
            sx={{ width: "100%", maxWidth: 400 }}
            data-testid="health-checks"
          >
            {Object.entries(data.checks).map(([name, check]) => (
              <CheckRow key={name} name={name} check={check} />
            ))}
          </Stack>
        </>
      )}
    </Box>
  );
}
