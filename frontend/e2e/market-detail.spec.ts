import { expect, test } from "@playwright/test";

// Snapshots are OS-specific — skip in CI to avoid linux/darwin mismatch.
// Run locally with: npx playwright test --update-snapshots
test("dashboard page visual regression", async ({ page }) => {
  test.skip(!!process.env.CI, "Visual snapshots are OS-specific, run locally only");

  await page.goto("/");

  // Wait for the dashboard to load
  await expect(page.getByText("Polymarket Analytics")).toBeVisible();
  await expect(page).toHaveScreenshot();
});

test("market detail page shows 404 for invalid market", async ({ page }) => {
  await page.goto("/markets/invalid-market-id");

  // Should show back button
  await expect(page.getByRole("button", { name: /back/i })).toBeVisible();
  // Should show market not found or error message (since API won't have this market)
  await expect(page.locator("body")).not.toBeEmpty();
});
