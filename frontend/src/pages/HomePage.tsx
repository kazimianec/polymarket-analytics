import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

export default function HomePage() {
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
      <Typography variant="h4">Welcome</Typography>
      <Typography variant="body1" color="text.secondary">
        Replace this page with your app.
      </Typography>
    </Box>
  );
}
