import { LightningElement, api } from "lwc";

const columns = [
  {
    label: "Code produit",
    fieldName: "codeproduit",
    hideDefaultActions: true,
    wrapText: true,
    sortable: true
  },
  {
    label: "Désignation",
    fieldName: "designation",
    hideDefaultActions: true,
    wrapText: true,
    sortable: true
  },
  {
    label: "Entrepôt",
    fieldName: "nomentrepot",
    hideDefaultActions: true,
    wrapText: true,
    sortable: true
  },
  {
    label: "Stock Physique",
    fieldName: "physique",
    type: "number",
    hideDefaultActions: true,
    wrapText: true,
    sortable: true
  },
  {
    label: "En commande",
    fieldName: "commande",
    type: "number",
    hideDefaultActions: true,
    wrapText: true,
    sortable: true
  },
  {
    label: "Disponible",
    fieldName: "disponible",
    type: "number",
    hideDefaultActions: true,
    wrapText: true,
    sortable: true
  }
];
// By default, display only the first 10 items of stocks array
const DEFAULT_START_ARRAY = 0;
const DEFAULT_END_ARRAY = 10;

export default class StockTable extends LightningElement {
  @api
  get stocks() {
    return this._stocks;
  }
  set stocks(value) {
    this._stocks = value;
  }
  _stocks;
  stocksToDisplay;
  cols = columns;
  sortDirection = "asc";
  sortedBy;
  maxRows = DEFAULT_END_ARRAY;

  handleChangeDisplay(event) {
    this.maxRows = event.detail.pageSize;
    this.setStocksToDisplay(event.detail);
  }

  setStocksToDisplay({ start = DEFAULT_START_ARRAY, end = this.maxRows } = {}) {
    if (this._stocks) {
      console.log(`START : ${start} ==== END : ${end}`);
      this.stocksToDisplay = this._stocks.slice(start, end);
    }
  }

  handleSortCols(event) {
    if (!this._stocks || this._stocks.length === 0) return;

    const { fieldName: sortedBy, sortDirection } = event.detail;
    const cloneData = [...this._stocks].sort(
      this.sortBy(sortedBy, sortDirection)
    );

    this._stocks = cloneData;
    this.setStocksToDisplay();
    this.template.querySelector("c-stock-paginator").setPagesAttributes();
    this.template.querySelector("c-stock-paginator").setControlClass();
    this.sortedBy = sortedBy;
    this.sortDirection = sortDirection;
  }

  sortBy(field, sortDirection) {
    const key = (x) => x[field];
    const reverse = sortDirection === "asc" ? 1 : -1;

    return function (a, b) {
      let aKey = key(a);
      let bKey = key(b);

      if (typeof a = "string") {
        aKey = aKey.toUpperCase();
        bKey = bKey.toUpperCase();
      }

      return (aKey === bKey ? 0 : aKey > bKey ? 1 : -1) * reverse;
    };
  }
}
