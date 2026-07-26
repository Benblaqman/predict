const FILE = "../data/dashboard.json";



async function loadDashboard(){


    const response = await fetch(FILE);


    const data = await response.json();



    document.getElementById(
        "totalSlips"
    ).innerHTML =
        data.overview.total_slips;



    document.getElementById(
        "safe"
    ).innerHTML =
        data.overview
        .risk_distribution
        .ULTRA_SAFE;



    document.getElementById(
        "medium"
    ).innerHTML =
        data.overview
        .risk_distribution
        .MEDIUM;



    document.getElementById(
        "high"
    ).innerHTML =
        data.overview
        .risk_distribution
        .HIGH;



    displayFeatured(
        data.featured_slip
    );


    displaySlips(
        data.slips
    );

}



function displayFeatured(
    slip
){


    if(!slip){

        return;

    }



    document.getElementById(
        "featured"
    ).innerHTML = createSlipHTML(
        slip
    );

}



function displaySlips(
    slips
){


    let html="";



    slips.forEach(
        slip => {

            html += createSlipHTML(
                slip
            );

        }

    );



    document.getElementById(
        "slips"
    ).innerHTML = html;

}




function createSlipHTML(
    slip
){


return `


<div class="slip ${slip.risk.toLowerCase()}">


<h3>

Slip ${slip.id}

</h3>


<p>

Risk:
<b>${slip.risk}</b>

</p>



<p>

Confidence:
${slip.confidence}%

</p>



<p>

Combined Odds:
${slip.combined_odds}

</p>



${

slip.matches.map(

match => `


<div class="match">


${match.teams}


<br>


Market:
<b>
${match.market}
</b>


<br>


Confidence:
${match.confidence}%


<br>


Odds:
${match.odds}


</div>


`

).join("")

}



</div>


`;

}



loadDashboard();
