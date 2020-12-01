app.document$.subscribe(function () {
    const links = document.links;

    for (const i = 0, linksLength = links.length; i < linksLength; i++) {
       if (links[i].hostname != window.location.hostname) {
           links[i].target = '_blank';
       }
    }
})