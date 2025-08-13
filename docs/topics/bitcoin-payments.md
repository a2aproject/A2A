# Bitcoin Payments and Wallet Delegation

This extension demonstrates how agents can advertise the ability to accept Bitcoin payments or delegate spend rights via PSBTs.

## Declaring Support

Agents expose the `payment` capability within their Agent Card. A minimal example:

```json
{
  "capabilities": {
    "payment": {
      "bitcoin": {
        "payTo": "bc1qexampleaddress12345",
        "network": "mainnet"
      }
    }
  }
}
```

## Delegation

For delegated spending, include a `delegation` object describing the maximum amount, expiry time, and PSBT template:

```json
{
  "capabilities": {
    "payment": {
      "bitcoin": {
        "payTo": "bc1qexampleaddress12345",
        "delegation": {
          "maxSatoshis": 10000,
          "expiry": "2030-01-01T00:00:00Z",
          "psbt": "cHNidP8BAHECAAAAAVDP..."
        }
      }
    }
  }
}
```

The receiving agent validates and partially signs the PSBT, returning the signed transaction to the requester.
