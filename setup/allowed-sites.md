# Sites the fetch opens

Your AI app or its Chrome add-on asks before it opens a new site. Allow these once ("always allow") and the fetch can run without stopping. Allow only what you need: if you never appraise in Kendall County, skip its sites.

Every site below is free and public except connectMLS and Infosparks, which use your own MRED sign-in. The fetch never signs in for you.

## Every property

| What | Domains |
|---|---|
| MLS listings (connectMLS) | connectmls.mredllc.com, connectmls2.mredllc.com |
| Market graphs (Infosparks) | mred.stats.10kresearch.com |
| FEMA flood map | msc.fema.gov |
| County and town map viewers | www.arcgis.com, utility.arcgis.com, services1.arcgis.com, services2.arcgis.com, services3.arcgis.com, services6.arcgis.com, services7.arcgis.com |
| PDF reader library | cdnjs.cloudflare.com |

## Cook County

| What | Domains |
|---|---|
| Recorded legal description | crs.cookcountyclerkil.gov |
| Plat and parcel maps | maps.cookcountyil.gov, gis.cookcountyil.gov, cookcountyil.maps.arcgis.com |
| Tax page | www.cookcountypropertyinfo.com |
| Chicago zoning | gisapps.chicago.gov |
| Suburban zoning (GIS Consortium towns) | ags.gisconsortium.org, communitymapviewer.gisconsortium.org |

## DuPage County

| What | Domains |
|---|---|
| Recorded legal description | recorder.dupageco.org |
| Plat and zoning maps | gis.dupageco.org |
| Township assessors | search.addisontownship.com, mybtao.com, propertysearch.mybtao.com, search.dgtownship.com, lisletownshipassessor.com, miltonassessor.com, napervilletownship.com, www.waynetownshipassessor.com, search.winfieldtownship.com, search.yorkassessor.com |

## Kane County

| What | Domains |
|---|---|
| Recorded legal description | lrs.kanecountyrecorder.net, imagesite-kane-prod.land-code.com |
| Plat and zoning maps | gistech.countyofkane.org, kanecountyil.gov |
| Township assessors | search.auroratownshipassessor.com, search.bataviatownship.com, search.blackberrytwpil.gov, www.camptontownship.com, search.dundeetownship.com, search.elgintownship.com, www.kanevilletownship.com, platotownshipassessor.com, platotwp.gov, www.stctownshipassessor.org |

## Lake County

| What | Domains |
|---|---|
| Plat and zoning maps | maps.lakecountyil.gov |

## McHenry County

| What | Domains |
|---|---|
| Plat and zoning maps | www.mchenrycountygis.org |
| Tax page | mchenryil.devnetwedge.com |
| Township assessors | property.atasr.org, burtontwp.com, chemungtownshipil.gov, www.coraltownship.com, search.dorrtownship.com, graftontownship.us, search.greenwoodtownshipil.gov, search.mchenrytownship.com, search.nundatownship.com, rileytwp.com, senecatownship.com |

## Will County

| What | Domains |
|---|---|
| Property card, plat and zoning | gis.willcountyillinois.com, www.willcountysoa.com |
| Township assessors | www.dupagetownshipassessor.com, 1968-30268.el-alt.com, search.frankfortassessor.com, www.homerassessor.org, search.jacksontownshipil.com, jolietassessor.net, www.lockporttownshipassessor.com, manhattantownship.com, moneeassessor.com, app.plainfieldassessor.com, www.troytownship.com, troytownship.com, wheatlandassessor.com |

## Kendall County

| What | Domains |
|---|---|
| Plat and zoning maps | maps.co.kendall.il.us, kcgis-tax-maps.s3.us-east-2.amazonaws.com |
| Township assessors | www.bristoltownshipassessor.com, search.oswegotownship.com |

## DeKalb County

| What | Domains |
|---|---|
| Recorded legal description | lrs.dekalbrecorder.com |
| Plat and zoning maps | spatial.dekalbcounty.org |
| Township assessors | dekalbtownshipassessor.com |

## Village and city zoning maps

Outside Chicago, the zoning map often comes from the village or city's own site (`playbook\recipes\municipal-zoning.md`). The first time a new town comes up, your AI app asks to open its site. Check that it is the town's own site, then allow it.

If a township site moves or a new one turns up, the fetch adds it to `playbook\townships.json`.
