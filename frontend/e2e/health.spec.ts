import { expect, test } from "@playwright/test";

test("health page shows status chip", async ({ page }) => {
  await page.goto("/health");

  const chip = page.getByTestId("health-status");
  await expect(chip).toBeVisible();
});

test("health page shows ok status when API is up", async ({ page }) => {
  await page.goto("/health");

  const chip = page.getByTestId("health-status");
  await expect(chip).toHaveText("ok");
});

test("health page shows app name", async ({ page }) => {
  await page.goto("/health");

  await expect(page.getByText("fullstack-template")).toBeVisible();
});

test("health page shows env badge", async ({ page }) => {
  await page.goto("/health");

  const envChip = page.getByTestId("health-env");
  await expect(envChip).toBeVisible();
  const text = await envChip.innerText();
  expect(text.length).toBeGreaterThan(0);
});

test("health page shows runtime badge", async ({ page }) => {
  await page.goto("/health");

  await expect(page.getByTestId("health-runtime")).toBeVisible();
});

test("health page shows checks section with database", async ({ page }) => {
  await page.goto("/health");

  const checks = page.getByTestId("health-checks");
  await expect(checks).toBeVisible();
  await expect(checks.getByText("database")).toBeVisible();
});

// Snapshots are OS-specific — skip in CI to avoid linux/darwin mismatch.
// Run locally with: npx playwright test --update-snapshots
test("health page visual regression", async ({ page }) => {
  test.skip(!!process.env.CI, "Visual snapshots are OS-specific, run locally only");

  await page.goto("/health");

  await expect(page.getByTestId("health-status")).toBeVisible();
  await expect(page).toHaveScreenshot();
});
