# Visualizations API Reference

The Visualizations API provides CRUD endpoints for managing standalone visualizations using dataView datasets.

> **ES|QL visualizations cannot be created or updated via this API.** Use inline panels in the Dashboard API instead.
> See [Chart Types Reference](chart-types-reference.md) for ES|QL panel schemas.

## Endpoints

### List Visualizations

```http
GET /api/visualizations?query=&page=&per_page=
Header: Elastic-Api-Version: 2023-10-31
```

| Parameter      | Type   | Description                      |
| -------------- | ------ | -------------------------------- |
| `query`        | string | Search query                     |
| `searchFields` | string | Fields to search (e.g., `title`) |
| `page`         | number | Page number (default: 1)         |
| `per_page`     | number | Results per page (default: 100)  |

### Get Visualization

```http
GET /api/visualizations/:id
Header: Elastic-Api-Version: 2023-10-31
```

### Create Visualization

```http
POST /api/visualizations
Header: Elastic-Api-Version: 2023-10-31
```

`POST` does not accept an `id` parameter. The API auto-generates one.

```json
{
  "type": "metric",
  "data_source": {
    "type": "data_view_reference",
    "ref_id": "90943e30-9a47-11e8-b64d-95841ca0b247"
  },
  "metrics": [{ "type": "primary", "operation": "count" }]
}
```

### Update Visualization (Upsert)

`PUT` supports upsert — creates the visualization if it does not exist, or updates it if it does.

```http
PUT /api/visualizations/:id
Header: Elastic-Api-Version: 2023-10-31
```

### Delete Visualization

```http
DELETE /api/visualizations/:id
Header: Elastic-Api-Version: 2023-10-31
```

## Response Envelope

```json
{
  "id": "uuid",
  "data": {
    /* visualization definition */
  },
  "meta": {
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "created_by": "user_id",
    "updated_by": "user_id",
    "managed": false
  }
}
```

Search results wrap items in a `data` array with pagination in `meta` (`page`, `per_page`, `total`).

## Common Properties

| Property                | Type    | Description                               |
| ----------------------- | ------- | ----------------------------------------- |
| `type`                  | string  | Chart type (required)                     |
| `data_source`           | object  | Data source configuration (required)      |
| `sampling`              | number  | Sampling rate 0-1 (default: 1)            |
| `ignore_global_filters` | boolean | Ignore dashboard filters (default: false) |

The API injects sensible defaults for omitted properties — clients can send minimal payloads.
