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
    ["Serie", "Patroon", "Periode"].forEach(function (item, index) {
        let optionCount = $("#" + item + " option").length;
        let selectedSeries = $("#" + item).val();
        choices[item] = {"total": optionCount,
                           "options": selectedSeries}
    })
    console.log(choices)

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
    console.log(data)

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

// 
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
    button1.innerHTML = "Herbereken Relevantie";
    col1.appendChild(button1);

    let button2 = document.createElement("button");
    button2.className = "btn btn-success buttonModC";
    button2.setAttribute("id", "button2ModC");
    button2.innerHTML = "Generate Article!";
    col2.appendChild(button2);

    // Add functionality to both buttons 
    $('#button1ModC').on('click', function() {
        alert("Herberekenen!!");
    })

   $('#button2ModC').on('click', function() {
        generateArticle();
    })
}


//
async function generateArticle() {
    // generate a new article
    let response = await fetch('api/articles/generate');
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

// /**
//  * sends a request to the specified url from a form. this will change the window location.
//  * @param {string} path the path to send the post request to
//  * @param {object} params the paramiters to add to the url
//  * @param {string} [method=post] the method to use on the form
//  */

// function post(path, params, method='post') {

//     // The rest of this code assumes you are not using a library.
//     // It can be made less wordy if you use one.
//     const form = document.createElement('form');
//     form.method = method;
//     form.action = path;
  
//     for (const key in params) {
//       if (params.hasOwnProperty(key)) {
//         const hiddenField = document.createElement('input');
//         hiddenField.type = 'hidden';
//         hiddenField.name = key;
//         hiddenField.value = params[key];
  
//         form.appendChild(hiddenField);
//       }
//     }
  
//     document.body.appendChild(form);
//     form.submit();
//   }
  

// MODULE A timeseries
async function renderModuleA() {
    let col = ["Serie", "Oudste datum", "Recentste datum", "Laatste koers"]

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
        rows.push([key, info['min_date'], info['max_date'], info['close']]);
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
    section1.className = "row justify-content-center h-40 w-100 slider-container"
    contentDiv.appendChild(section1); 

    let linkSection = document.createElement("div");
    linkSection.className = "row justify-content-end w-100 relev-button"
    contentDiv.appendChild(linkSection);

    let section2 = document.createElement("div");
    section2.className = "row justify-content-center h-40 w-100"
    contentDiv.appendChild(section2);

    let section3 = document.createElement("div");
    section3.className = "row justify-content-center h-20 w-100"
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