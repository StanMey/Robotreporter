// Static variables
const moduleView = ".module-view";
const moduleContent = ".module-content";
let lineChart;


// clean the content of a div element
function clearDivContent(target) {
    document.querySelector(target).innerHTML = ""
}

// 
function highLightSelectedButton(buttonNumber) {

    // set all the buttons to the same color
    let all_buttons = document.querySelectorAll(".btn-menu");
    all_buttons.forEach(
        function(elem, currentIndex, parent) {
            elem.style.backgroundColor = "#F5F5F5";
            elem.style.color = "#000000";
        }
    );
    
    // change the color of the button that is currently selected
    const buttons = [".btn-mod-a", ".btn-mod-b", ".btn-mod-c", ".btn-mod-d"];
    const colors = ["#2a9d8f", "#e9c46a", "#f4a261", "#80d8d5"];
    let selected_button = document.querySelector(buttons[buttonNumber]);
    selected_button.style.backgroundColor = colors[buttonNumber];
    selected_button.style.color = "#FFFFFF";
}

// 
async function createFilterMenuModB(contentDiv) {

    // get all available filters
    let response = await fetch('api/observations/getfilters');
    let filters = await response.json(); 

    // let filters = {"Serie": ["AMX", "Aalberts", "postnl", "basic fit"],
    //                 "Patroon": ["Stijging", "Daling"],
    //                 "Periode" : ["Vorige dag", "Deze week", "Deze maand"]}

    // build all the filter selects
    for(key in filters) {
        let selectList = document.createElement("select");
        selectList.id = key;
        selectList.multiple = true;
        contentDiv.appendChild(selectList);

        for(let i = 0; i < filters[key].length; i++) {
            let option = document.createElement("option");
            option.value = filters[key][i];
            option.text = filters[key][i];
            selectList.appendChild(option);
        }
    }
    // build the filter button
    let filterButton = document.createElement("button");
    filterButton.id = "modBFilterButton";
    filterButton.className = "btn btn-primary"
    filterButton.innerHTML = "Filter";
    contentDiv.appendChild(filterButton);

    // activate multiselect on the filters
    // http://davidstutz.github.io/bootstrap-multiselect/
    for(key in filters) {
        $(`#${key}`).multiselect({
            includeSelectAllOption: true,
            nonSelectedText: key
        })
    }

    // Add function to 
    $('#modBFilterButton').on('click', function() {
        applyFiltersModB();
    })
}

// 
async function applyFiltersModB() {

    let choices = {};
    // get the selected values
    ["Serie", "Sector", "Patroon", "Periode"].forEach(function (item, index) {
        let optionCount = $("#" + item + " option").length;
        let selectedSeries = $("#" + item).val();
        choices[item] = {"total": optionCount,
                           "options": selectedSeries}
    })

    const url = "api/observations/usefilters";
    const csrftoken = Cookies.get('csrftoken');

    let response = await fetch(url, {
        method: "POST",
        headers: {
            "X-CSRF-Token": csrftoken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(choices),
        mode: "same-origin"
    })
    let data = await response.json();

    const col = ["Serie", "Periode", "Patroon", "Zin"]

    dataTable = document.getElementById("datatable_sec");
    dataTable.innerHTML = "";

    // format it to the form of: [["AMX", "1-9-2020/8-9-2020", "Stijging", "Gestegen met 5.00%"].....]
    let rows = []
    for (key in data) {
        obj = data[key]
        rows.push([obj['serie'], obj['period'], obj['pattern'], obj['observation']]);
    }
    createDataTable(dataTable, "observations_table", col, rows, false);

}

async function createFilterMenuModC(contentDiv) {

    // get all available filters
    let response = await fetch('api/relevance/getfilters');
    let filters = await response.json(); 

    // build all the filter selects
    for(key in filters) {
        let selectList = document.createElement("select");
        selectList.id = key;
        selectList.multiple = true;
        contentDiv.appendChild(selectList);

        for(let i = 0; i < filters[key].length; i++) {
            let option = document.createElement("option");
            option.value = filters[key][i];
            option.text = filters[key][i];
            selectList.appendChild(option);
        }
    }

    // activate multiselect on the filters
    // http://davidstutz.github.io/bootstrap-multiselect/
    for(key in filters) {
        $(`#${key}`).multiselect({
            includeSelectAllOption: true,
            nonSelectedText: key
        })
    }
}


// GENERATING THE TABLES
// https://www.valentinog.com/blog/html-table/
// generate table head
function generateTableHead(table, columns) {
    let thead = table.createTHead();
    let row = thead.insertRow();

    for (col of columns) {
        let th = document.createElement("th");
        let text = document.createTextNode(col);
        th.appendChild(text);
        row.appendChild(th);
    }
}

// insert values into the table
function generateTableRows(table, data) {
    for (element of data) {
        let row = table.insertRow();
        for (let i = 0; i < element.length; i++) {
            let cell = row.insertCell();
            let text = document.createTextNode(element[i]);
            cell.appendChild(text);
        }
    }
}
// create the whole table
function createDataTable(table, id, columns, data, modA) {
    let tableDiv = document.createElement("div");
    tableDiv.className = "row table-responsive";
    tableDiv.setAttribute("id", id);
    table.appendChild(tableDiv);

    let tbl = document.createElement("table");
    tbl.className = "table table-bordered";
    tbl.setAttribute("id", "datatable");
    tableDiv.appendChild(tbl);

    generateTableRows(tbl, data);
    generateTableHead(tbl, columns);
    
    // create the Datatable with jquery
    let dataTable = $('#datatable').DataTable();

    if (modA) {
        // Add a classname to make the table interactive
        tableDiv.className += " mod-a-table";

        // Add a method to each row to update the graph this method only applies on module A
        $('#datatable tbody').on('click', 'tr', async function() {
            let serie_name = dataTable.row( this ).data();

            let response = await fetch("api/dataseries/" + serie_name[0] + "/close");
            let data = await response.json();

            lineChart.updateClose(data, serie_name[0]);
        })
    }
}

// class for creating a line chart with d3.js
// https://www.d3-graph-gallery.com/graph/line_basic.html
// https://www.d3-graph-gallery.com/graph/line_change_data.html
// https://bl.ocks.org/curran/923f33c78a80d8785a974507693a6f21
class LineChart {
    constructor(contentDiv) {
        this.contentDiv = contentDiv;
    }

    build() {
        this.contentDiv.id = "my_dataviz";
        this.wWidth = document.getElementById("my_dataviz").offsetWidth * 0.7;

        this.margin = {top: 30, right: 30, bottom: 30, left: 40};
        this.width = this.wWidth - this.margin.left - this.margin.right;
        this.height = 350 - this.margin.top - this.margin.bottom;
    }
    
    updateClose(data, serie_name) {

        document.getElementById('my_dataviz').innerHTML = '';

        // append the svg object to the body of the page
        let svg = d3.select("#my_dataviz")
        .append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
        .append("g")
            .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

        // setting the parser
        let parseTime = d3.timeParse("%d-%m-%Y");

        // loading in the data
        let dataset = data
            .map(function(d) {
                return {
                    date: parseTime(d.date),
                    value: d.value
                };
            })
        
        let valueX = function(d) { return new Date(d.date)};
        let valueY = function(d) { return d.value};
        
        // adding x-axis
        let scaleX = d3.scaleTime()
            .domain(d3.extent(dataset, valueX))
            .range([0, this.width]);
        svg.append("g")
            .attr("transform", "translate(0," + this.height + ")")
            .call(d3.axisBottom(scaleX));
        
        // adding y-axis
        var scaleY = d3.scaleLinear()
            .domain(d3.extent(dataset, valueY))
            .range([this.height, 0]);
        svg.append("g")
            .call(d3.axisLeft(scaleY));
        
        // setting up the line
        let line = d3.line()
            .x(function(d) { return scaleX(valueX(d)); })
            .y(function(d) { return scaleY(valueY(d)); })

        // adding the line
        svg.append("path")
            .attr("d", line(dataset))
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-width", 1.5)
        
        svg.append("text")
            .attr("x", (this.width / 2))             
            .attr("y", 0 - (this.margin.top / 2))
            .attr("text-anchor", "middle")  
            .style("font-size", "16px")
            .style("text-decoration", "underline") 
            .text("Koers " + serie_name);
        }

    updateTransitionClose(data) {
        // TODO
        // add a transition and update the data every time without completely destroying the graph
    }
}


// 
function createImportanceSliders(contentDiv) {
    let col1 = document.createElement("div");
    col1.className = "col d-flex justify-content-center";
    contentDiv.appendChild(col1);

    let col2 = document.createElement("div");
    col2.className = "col d-flex justify-content-center";
    contentDiv.appendChild(col2);

    createSingleSlider(col1, "Stijgers");
    createSingleSlider(col2, "Dalers");

}

// 
function createSingleSlider(contentDiv, title) {
    let sliderCont = document.createElement("div");
    sliderCont.className = "slidercontainer text-center";
    contentDiv.appendChild(sliderCont);

    let sliderTitle = document.createElement("h6");
    sliderTitle.className = "text-muted";
    sliderTitle.innerHTML = title;
    sliderCont.appendChild(sliderTitle);

    let sliderInput = document.createElement("input");
    sliderInput.type = "range";
    sliderInput.min = "0";
    sliderInput.max = "10";
    sliderInput.value = "5";
    sliderInput.className = "slider";
    sliderCont.appendChild(sliderInput);
}

/**
 * Multiple lines of JSDoc text are written here,
 * wrapped normally.
 * @param {string} contentDiv The class name of the div where the buttons should be loaded in.
 */
async function createButtonsModC(contentDiv) {
    let col1 = document.createElement("div");
    col1.className = "col d-flex justify-content-center";
    contentDiv.appendChild(col1);

    let col2 = document.createElement("div");
    col2.className = "col d-flex justify-content-center";
    contentDiv.appendChild(col2);

    let button1 = document.createElement("button");
    button1.className = "btn btn-success buttonModC";
    button1.setAttribute("id", "button1ModC");
    button1.innerHTML = "Stel artikel samen";
    col1.appendChild(button1);

    let button2 = document.createElement("button");
    button2.className = "btn btn-success buttonModC";
    button2.setAttribute("id", "button2ModC");
    button2.innerHTML = "Genereer artikel!";
    col2.appendChild(button2);

    // Add functionality to both buttons 
    $('#button1ModC').on('click', function() {
        loadComposeView();
    })

   $('#button2ModC').on('click', function() {
        generateArticle();
    })
}


/**
 * When the button 'generate article' is clicked, the filters that apply are read,
 * Eventually a new article will be generated and the user is redirected to a page with the article. 
 */
async function generateArticle() {
    // search for the filters that have been selected
    let choices = {};
    // get the selected values
    ["Sector", "Periode"].forEach(function (item, index) {
        let optionCount = $("#" + item + " option").length;
        let selectedSeries = $("#" + item).val();
        choices[item] = {"total": optionCount,
                           "options": selectedSeries}
    })
    choices["manual"] = false;

    // generate a new article and pass in the filters
    const url = "api/articles/generate";
    const csrftoken = Cookies.get('csrftoken');

    let response = await fetch(url, {
        method: "POST",
        headers: {
            "X-CSRF-Token": csrftoken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(choices),
        mode: "same-origin"
    })
    let data = await response.json();

    // get the id of the article and redirect to the article
    _id = data['article_number']
    window.open('/module/articles/' + _id, target="_self");
}


/**
 * When
 */
async function loadComposeView() {
    // search for the filters that have been selected
    let choices = {};
    // get the selected values
    ["Sector", "Periode"].forEach(function (item, index) {
        let optionCount = $("#" + item + " option").length;
        let selectedSeries = $("#" + item).val();
        choices[item] = {"total": optionCount,
                           "options": selectedSeries}
    })
    choices["manual"] = true;

    // generate a new article and pass in the filters
    const url = "api/articles/composeoptions";
    const csrftoken = Cookies.get('csrftoken');

    let response = await fetch(url, {
        method: "POST",
        headers: {
            "X-CSRF-Token": csrftoken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(choices),
        mode: "same-origin"
    })
    let data = await response.json();

    setUpComposerView(moduleContent);
    buildComposerView(data, choices);
}

/**
 * Build the div layout of where the selection datatables are to be.
 * @param {String} contentDiv The class where all the div's have to be build under.
 */
function setUpComposerView(contentDiv) {

    document.querySelector(contentDiv).innerHTML = ""

    let contentViewDiv = document.querySelector(contentDiv);

    let tablesDiv = document.createElement("div");
    tablesDiv.className = "row compose-view";
    contentViewDiv.appendChild(tablesDiv);

    leftTableDiv = document.createElement("div");
    leftTableDiv.className = "col table-responsive left-compose-table";
    tablesDiv.appendChild(leftTableDiv);

    rightTableDiv = document.createElement("div");
    rightTableDiv.className = "col table-responsive right-compose-table justify-content-center";
    tablesDiv.appendChild(rightTableDiv);
}


/**
 * Builds the actual selection datatables and implements all the functionality.
 * @param {dict} data A JSON dictionary with all the data.
 * @param {dict} filters The filters the user has selected.
 */
function buildComposerView(data, filters) {
    let selectedObservs = [];
    let order = 1;

    let leftTableDiv = document.querySelector(".left-compose-table")
    let rightTableDiv = document.querySelector(".right-compose-table");

    // build the titles of the datatables
    let leftText = document.createElement("h3");
    leftText.innerHTML = "Observaties";
    leftTableDiv.appendChild(leftText);

    let rightText = document.createElement("h3");
    rightText.innerHTML = "Geselecteerde zinnen";
    rightTableDiv.appendChild(rightText);

    // create the input for the title
    let formGroup = document.createElement("div");
    formGroup.className = "form-group";
    rightTableDiv.appendChild(formGroup);
    
    let titleLabel = document.createElement("label");
    titleLabel.setAttribute("for", "title-pick");
    titleLabel.innerHTML = "Titel:";
    formGroup.appendChild(titleLabel);

    let titleInput = document.createElement("input");
    titleInput.setAttribute("type", "text");
    titleInput.className = "form-control";
    titleInput.setAttribute("id", "title-pick");
    formGroup.appendChild(titleInput);

    // create the datatables
    let leftTbl = document.createElement("table");
    leftTbl.className = "table table-bordered";
    leftTbl.setAttribute("id", "leftDatatable");
    leftTableDiv.appendChild(leftTbl);

    let rightTbl = document.createElement("table");
    rightTbl.className = "table table-bordered";
    rightTbl.setAttribute("id", "rightDatatable");
    rightTableDiv.appendChild(rightTbl);

    // create the construct button
    let constructButton = document.createElement("button");
    constructButton.className = "btn btn-success compose-button";
    constructButton.setAttribute("id", "compose-text-button");
    constructButton.innerHTML = "Bouw artikel!";
    rightTableDiv.appendChild(constructButton);

    // format the data
    let rows = []
    for (key in data) {
        obj = data[key]
        rows.push([obj['pattern'], obj['sector'], obj['period'], obj['relevance'], obj['observation']]);
    }

    // create the left DataTable
    let leftTableColumns = ["patroon", "sector", "periode", "relevantie", "observatie"];
    generateTableRows(leftTbl, rows);
    generateTableHead(leftTbl, leftTableColumns);

    // create the Datatable with jquery
    let ldataTable = $('#leftDatatable').DataTable({
        "scrollY": "550px",
        "scrollCollapse": true
    });

    // create the right DataTable
    let rightTableColumns = ["zin nummer", "observatie"];
    generateTableRows(rightTbl, []);
    generateTableHead(rightTbl, rightTableColumns);

    // create the Datatable with jquery
    let rdataTable = $('#rightDatatable').DataTable({
        "scrollY": "550px",
        "scrollCollapse": true
    });

    // add functionality to both the datatables
    $('#leftDatatable tbody').on('click', 'tr', async function() {
        // retrieve the data from the row
        let observation = ldataTable.row( this ).data();

        // add the observation to the article table and save it
        selectedObservs.push(observation);
        let newRow = [order, observation[4]];
        order = selectedObservs.length + 1;

        rdataTable.row.add(newRow).draw( false );

        // recalculate the new order of the data
        newData = []
        for (let x = 0; x < selectedObservs.length; x++) {
            newData.push([x+1, selectedObservs[x][4]]);
        }

        // clear the datatable and reinsert the new data
        rdataTable.clear().rows.add(newData).draw();

        // remove the observation from the left table
        ldataTable.row( this ).remove().draw();
    });

    $('#rightDatatable tbody').on('click', 'tr', async function() {
        // retrieve the data from the row
        let observation = rdataTable.row( this ).data();
        let index = observation[0];

        // remove observation out of saved observations
        selectedObservs.splice(index-1, 1);

        // recalculate the new order of the data
        newData = []
        for (let x = 0; x < selectedObservs.length; x++) {
            newData.push([x+1, selectedObservs[x][4]]);
        }

        // clear the datatable and reinsert the new data
        rdataTable.clear().rows.add(newData).draw();
    });

    // Add functionality to generate article button
    $('#compose-text-button').on('click', function() {
        // get the title
        title = document.getElementById("title-pick").value;
        // construct the article
        constructArticle(title, selectedObservs, filters);
    })
}


/**
 * Send the sentences that the user has chosen back to the back-end so that the article can be constructed.
 * @param {string} title The title of the article.
 * @param {Array} content All the sentences the user has chosen.
 * @param {dict} filters The filters the user has selected.
 */
async function constructArticle(title, content, filters) {

    // construct a new article and pass in the filters
    const url = "api/articles/composearticle";
    const csrftoken = Cookies.get('csrftoken');

    let response = await fetch(url, {
        method: "POST",
        headers: {
            "X-CSRF-Token": csrftoken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({'title': title,
                              'content': content,
                              'filters': filters}),
        mode: "same-origin"
    })
    let data = await response.json();

    // get the id of the article and redirect to the article
    _id = data['article_number']
    window.open('/module/articles/' + _id, target="_self");
}


// 
function buildArticleCard(contentDiv, content) {

    let _id = content['article_id']

    let card = document.createElement("div");
    card.className = "card";
    contentDiv.appendChild(card);

    let cardBody = document.createElement("div");
    cardBody.className = "card-body";
    card.appendChild(cardBody);

    let cardTitle = document.createElement("h5");
    cardTitle.className = "card-title";
    cardTitle.innerHTML = content["title"];
    cardBody.appendChild(cardTitle);

    let cardSubTitle = document.createElement("h6");
    cardSubTitle.className = "card-subtitle mb-2 text-muted";
    cardSubTitle.innerHTML = content["date_show"];
    cardBody.appendChild(cardSubTitle);

    let cardText = document.createElement("p");
    cardText.className = "card-text";
    cardText.innerHTML = content["content"].substring(0, 200) + ".....";
    cardBody.appendChild(cardText);

    let cardLink = document.createElement("a");
    cardLink.className = "card-link";
    cardLink.setAttribute("id", "article_id_" + _id)
    cardLink.innerHTML = "Naar artikel";
    cardBody.appendChild(cardLink);

    $('#article_id_' + _id).on('click', function() {
        window.open('/module/articles/' + _id, target="_self");
    })
}

// 
function buildArticlesModD(contentDiv, content) {
    // 
    let rowAmount = 2;
    let articlesPerRow = 3;

    // 
    let counter = 1
    for (let i = 0; i < rowAmount; i++) {
        let row = document.createElement("div");
        row.className = "row w-100 articles-row"
        contentDiv.appendChild(row);

        //
        for (let j = 0; j < articlesPerRow; j++) {
            let colDiv = document.createElement("div")
            colDiv.className = "col";
            row.appendChild(colDiv);

            buildArticleCard(colDiv, content[counter]);
            counter += 1
        }
    }
}
  

// MODULE A timeseries
async function renderModuleA() {
    let col = ["Serie", "sector", "Oudste datum", "Recentste datum", "Laatste koers"]

    clearDivContent(moduleContent);
    highLightSelectedButton(0);

    let contentDiv = document.querySelector(moduleContent);

    let section1 = document.createElement("div");
    section1.className = "row justify-content-center h-50 w-100";
    contentDiv.appendChild(section1)

    let section2 = document.createElement("div");
    section2.className = "row justify-content-center h-50 w-100";
    contentDiv.appendChild(section2)

    lineChart = new LineChart(section1);
    lineChart.build();

    let amxResponse = await fetch("api/dataseries/AMX/close");
    let data1 = await amxResponse.json();

    lineChart.updateClose(data1, "AMX")

    // get all information about the available dataseries from db
    let dataseriesResponse = await fetch('api/dataseries');
    let data2 = await dataseriesResponse.json();
    
    // format it to the form of: [["AMX", "1-9-20", "8-9-20", "43.5"],......]
    let rows = []
    for (key in data2) {
        info = data2[key];
        rows.push([key, info['sector'], info['min_date'], info['max_date'], info['close']]);
    }

    createDataTable(section2, "timeseries_table", col, rows, true);
}


// MODULE B Observations
async function renderModuleB() {
    clearDivContent(moduleContent);
    highLightSelectedButton(1);

    let contentDiv = document.querySelector(moduleContent);

    let section1 = document.createElement("div");
    section1.className = "row justify-content-center h-50 w-100"
    contentDiv.appendChild(section1)

    let section2 = document.createElement("div");
    section2.className = "row justify-content-center h-50 w-100"
    section2.id = "datatable_sec";
    contentDiv.appendChild(section2)

    let col = ["Serie", "Periode", "Patroon", "Zin"]

    // get all information about the available dataseries from db
    let response = await fetch('api/observations/latest');
    let data = await response.json();

    // format it to the form of: [["AMX", "1-9-2020/8-9-2020", "Stijging", "Gestegen met 5.00%"].....]
    let rows = []
    for (key in data) {
        obj = data[key]
        rows.push([obj['serie'], obj['period'], obj['pattern'], obj['observation']]);
    }

    createFilterMenuModB(section1);
    createDataTable(section2, "observations_table", col, rows, false);
}


// MODULE C Observations-relevance
async function renderModuleC() {
    clearDivContent(moduleContent);
    highLightSelectedButton(2);

    let contentDiv = document.querySelector(moduleContent);

    let section1 = document.createElement("div");
    section1.className = "row justify-content-center h-40 w-100 filter-container"
    contentDiv.appendChild(section1); 

    let linkSection = document.createElement("div");
    linkSection.className = "row justify-content-end w-100 relev-button"
    contentDiv.appendChild(linkSection);

    let section2 = document.createElement("div");
    section2.className = "row justify-content-center h-40 w-100"
    contentDiv.appendChild(section2);

    let section3 = document.createElement("div");
    section3.className = "row justify-content-center h-20 w-100 generate-links"
    contentDiv.appendChild(section3);

    // add the link to the relevance page
    let link = document.createElement("a");
    link.setAttribute("href", "/module/relevance");
    link.className = "justify-content-end";
    link.textContent = "Relevantie?";
    linkSection.appendChild(link);

    let col = ["Serie", "Periode", "Patroon", "Zin", "Relevantie"]

    // get all information about the available dataseries from db
    let response = await fetch('api/observations/relevance');
    let data = await response.json();

    // format it to the form of: [["AMX", "1-9-2020/8-9-2020", "Stijging", "Gestegen met 5.00%", 8].....]
    let rows = []
    for (key in data) {
        obj = data[key]
        rows.push([obj['serie'], obj['period'], obj['pattern'], obj['observation'], obj['relevance']]);
    }

    // createImportanceSliders(section1);
    createFilterMenuModC(section1);
    createDataTable(section2, "obser_relev_table", col, rows, false);
    createButtonsModC(section3);
}


// MODULE D Articles
async function renderModuleDArticles() {
    clearDivContent(moduleContent);
    highLightSelectedButton(3);

    let contentDiv = document.querySelector(moduleContent);

    // get all information about the available dataseries from db
    let response = await fetch('api/articles');
    let data = await response.json();

    buildArticlesModD(contentDiv, data);
}