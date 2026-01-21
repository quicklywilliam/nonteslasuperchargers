# Non-Tesla Supercharger Data

A compact lookup file of Tesla Supercharger stations in the US that are compatible with non-Tesla vehicles. This data is intended to be combined with other data sources (ie [NREL's Alternative Fuel Stations API](https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/)) that do not include non-Tesla compatibility data.

## Data

**`compatible-stations.json`** (~21KB) contains geohash-6 codes for compatible stations:

```json
{
  "nacs": ["9q8yyk", "9q5ctr", ...],
  "ccs": ["dr5reg", "9qh0yz", ...]
}
```

- **nacs**: Stations with "NACS Partner Enabled" - non-Tesla vehicles with NACS ports can charge here
- **ccs**: Stations with "All Vehicles" access - CCS adapters (Magic Dock) available

## Usage

To check if a station at `(lat, lng)` is compatible:

1. Convert coordinates to a geohash-6 string
2. Check if it exists in the `nacs` or `ccs` array
3. Also check the 8 adjacent geohashes to handle cell boundary edge cases

### Example (JavaScript)

```javascript
import geohash from 'ngeohash';
import data from './compatible-stations.json';

function getCompatibility(lat, lng) {
  const hash = geohash.encode(lat, lng, 6);
  const neighbors = geohash.neighbors(hash);
  const toCheck = [hash, ...Object.values(neighbors)];

  const isNacs = toCheck.some(h => data.nacs.includes(h));
  const isCcs = toCheck.some(h => data.ccs.includes(h));

  return { nacs: isNacs, ccs: isCcs };
}
```

### Example (Swift)

```swift
import GeohashKit

func getCompatibility(lat: Double, lng: Double, data: StationData) -> (nacs: Bool, ccs: Bool) {
    let hash = Geohash.encode(latitude: lat, longitude: lng, precision: 6)
    let neighbors = Geohash.neighbors(hash)
    let toCheck = [hash] + neighbors

    let isNacs = toCheck.contains { data.nacs.contains($0) }
    let isCcs = toCheck.contains { data.ccs.contains($0) }

    return (nacs: isNacs, ccs: isCcs)
}
```

## Why geohash-6?

Geohash-6 cells are approximately 600m × 600m, which allows for fuzzy matching when comparing station locations from different data sources. This is intentional, since exact station coordinates may differ by data source.

## Data Updates

The data is refreshed daily via GitHub Actions. The scraper fetches from Tesla's API and filters for US stations with non-Tesla compatibility.

## Raw Data

`stations.json` contains the full raw response from Tesla's API for debugging purposes.
