import { expect, test } from "@playwright/test";

test("hero matches the product landing structure and remains usable on desktop", async ({ page }, testInfo) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Every MD paper.");
  await expect(page.getByRole("heading", { name: "Drop a PDF here" })).toBeVisible();
  await expect(page.getByRole("button", { name: "browse files" })).toBeVisible();
  await expect(page.getByRole("group", { name: "Synthetic demonstration samples" }).getByRole("button")).toHaveCount(4);
  await page.screenshot({ path: testInfo.outputPath("desktop-landing.png"), fullPage: true });
});

test("each sample is functional, openly synthetic, and methods have individual evidence", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: /WT & E41A/ }).click();
  await expect(page.getByText("Synthetic multi-system example")).toBeVisible();
  await expect(page.getByText("SYNTHETIC SAMPLE")).toBeVisible();
  await expect(page.getByText("WT and E41A belong to different experiments.")).toBeVisible();
  await page.getByRole("button", { name: /310 K/ }).click();
  await expect(page.getByText("E41A production simulations were performed at 310 K.")).toBeVisible();
  await expect(page.getByRole("button", { name: /Download CSV/ })).toHaveCount(0);
  await page.getByRole("button", { name: /GROMACS standard MD/ }).click();
  await expect(page.getByText("Synthetic GROMACS example")).toBeVisible();
});

test("PDF upload sends multipart file and renders backend evidence on success", async ({ page }) => {
  await page.route("**/api/v1/analyze", async (route) => {
    const request = route.request();
    expect(request.method()).toBe("POST");
    expect(request.postDataBuffer()?.toString()).toContain('filename="trial.pdf"');
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { "access-control-allow-origin": "http://127.0.0.1:3000" },
      body: JSON.stringify({
        schema_version: "1.0",
        document: { filename: "trial.pdf", pages: 1 },
        method_candidates: [{
          id: "candidate-1", field: "MD engine", value: "GROMACS 2024.1", page: 1,
          excerpt: "Production used GROMACS 2024.1.", verification: "page_text_match_only",
          grouping_status: "unassigned",
        }],
        review_items: [],
        scientific_flags: [],
        disclaimer: "Evidence candidates, not confirmed simulation protocols.",
      }),
    });
  });
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await page.locator("#paper-file").setInputFiles({
    name: "trial.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-1.4 test fixture"),
  });
  await page.getByRole("button", { name: "Analyze PDF" }).click();
  await expect(page.getByText("trial.pdf", { exact: false }).first()).toBeVisible();
  await expect(page.getByText("Production used GROMACS 2024.1.")).toBeVisible();
  await expect(page.getByRole("button", { name: /Download JSON/ })).toBeVisible();
});

test("mobile layout exposes upload and sample controls without horizontal overflow", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "Drop a PDF here" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Umbrella sampling/ })).toBeVisible();
  const widths = await page.evaluate(() => ({
    document: document.documentElement.scrollWidth,
    window: window.innerWidth,
  }));
  expect(widths.document).toBeLessThanOrEqual(widths.window + 1);
  await page.screenshot({ path: testInfo.outputPath("mobile-landing.png"), fullPage: true });
});
