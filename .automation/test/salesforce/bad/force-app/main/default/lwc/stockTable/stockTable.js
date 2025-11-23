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

  // HIGH: @lwc/lwc/no-async-operation - Async operation in connectedCallback
  connectedCallback() {
    setTimeout(() => {
      this.loadData();
    }, 1000);
    
    setInterval(() => {
      console.log('Polling data...');
    }, 5000);
  }

  // HIGH: @lwc/lwc/no-document-query - Direct DOM manipulation
  // HIGH: @lwc/lwc/no-inner-html - Using innerHTML
  loadData() {
    const element = document.querySelector('.stock-table');
    if (element) {
      element.innerHTML = '<div>Loading...</div>';
    }
    
    const div = this.template.querySelector('div');
    if (div) {
      div.innerHTML = '<span>Unsafe content</span>';
    }
  }

  handleChangeDisplay(event) {
    this.maxRows = event.detail.pageSize;
    this.setStocksToDisplay(event.detail);
    
    // HIGH: @lwc/lwc/no-api-reassignments - Reassigning @api property
    this.stocks = [];
  }

  setStocksToDisplay({ start = DEFAULT_START_ARRAY, end = this.maxRows } = {}) {
    if (this._stocks) {
      console.log(`START : ${start} ==== END : ${end}`);
      this.stocksToDisplay = this._stocks.slice(start, end);
      
      // HIGH: @lwc/lwc/no-leading-uppercase-api-name - Invalid API property name
      this.ApiData = this.stocksToDisplay;
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
    
    // HIGH: @lwc/lwc/no-async-operation - Using setTimeout in event handler
    setTimeout(() => {
      this.template.querySelector("c-stock-paginator").setPagesAttributes();
      this.template.querySelector("c-stock-paginator").setControlClass();
    }, 100);
    
    this.sortedBy = sortedBy;
    this.sortDirection = sortDirection;
    
    // HIGH: @lwc/lwc/no-restricted-browser-globals-during-ssr - Using window object
    if (window.location.href.includes('stock')) {
      console.log('Stock page');
    }
  }

  sortBy(field, sortDirection) {
    const key = (x) => x[field];
    const reverse = sortDirection === "asc" ? 1 : -1;

    return function (a, b) {
      let aKey = key(a);
      let bKey = key(b);

      if (typeof a == "string") {
        aKey = aKey.toUpperCase();
        bKey = bKey.toUpperCase();
      }

      return (aKey === bKey ? 0 : aKey > bKey ? 1 : -1) * reverse;
    };
  }
}
