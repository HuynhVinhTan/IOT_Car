export function formatNumber(value?: number | null, fractionDigits = 2) {
  if (value === undefined || value === null) {
    return "N/A";
  }

  return value.toFixed(fractionDigits);
}

export function formatDistance(value?: number | null) {
  if (value === undefined || value === null) {
    return "N/A";
  }

  return `${value.toFixed(1)} cm`;
}
