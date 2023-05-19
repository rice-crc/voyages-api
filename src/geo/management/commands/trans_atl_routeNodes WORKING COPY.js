var routeNodes = [
	new L.LatLng(-21.140868798573788, 37.496337890625),
	new L.LatLng(-27.916766641249065, 42.978515625),
	new L.LatLng(-31.503629305773018, 35.33203125),
	new L.LatLng(0.4614207935306211, -8.624267578125),
	new L.LatLng(-31.05293398570514, 9.84375),
	new L.LatLng(-15.5701278526594, -5.614013671875),
	new L.LatLng(-15.114552871944102, 3.5595703125),
	new L.LatLng(-22.553147478403194, 5.756835937499999),
	new L.LatLng(-15.707662769583505, -9.228515625),
	new L.LatLng(-13.111580118251648, -11.271972656249998),
	new L.LatLng(-10.314919285813147, -9.986572265624998),
	new L.LatLng(-9.351512670895596, -5.042724609375),
	new L.LatLng(-10.703791711680724, -0.626220703125),
	new L.LatLng(-9.622414142924793, 7.476196289062499),
	new L.LatLng(-10.055402736564224, 1.845703125),
	new L.LatLng(-8.754794702435605, -5.009765625),
	new L.LatLng(1.2303741774326145, 2.28515625),
	new L.LatLng(3.447624666646865, -8.59130859375),
	new L.LatLng(-1.263325357489324, 7.261962890625),
	new L.LatLng(-36.738884124394296, 22.148437499999996),
	new L.LatLng(-7.972197714386866, -9.931640625),
	new L.LatLng(-0.6591651462894504, -27.5537109375),
	new L.LatLng(-3.7765593098768635, -22.3681640625),
	new L.LatLng(-6.620957270326323, -16.259765625),
	new L.LatLng(9.232248799418674, -17.6220703125),
	new L.LatLng(3.601142320158722, -18.984375),
	new L.LatLng(-11.39387923296741, -28.564453125),
	new L.LatLng(2.3504147112508305, -31.069335937499996),
	new L.LatLng(5.900188795584172, -13.403320312499998),
	new L.LatLng(-6.708253968671543, -27.94921875),
	new L.LatLng(7.264394325339779, -16.45751953125),
	new L.LatLng(-14.26438308756265, -34.23339843750001),
	new L.LatLng(-8.167993177231883, -34.12353515625),
	new L.LatLng(-14.051330743518163, -22.631835937499996),
	new L.LatLng(-20.2209657795223, -27.2021484375),
	new L.LatLng(-22.75592068148639, -33.134765625),
	new L.LatLng(-24.287026865376422, -39.111328125),
	new L.LatLng(-27.059125784374054, -28.740234375),
	new L.LatLng(-32.990235559651055, -35.77148437499999),
	new L.LatLng(-37.71859032558814, -50.185546875),
	new L.LatLng(0.8349313860427184, -40.38574218750001),
	new L.LatLng(15.029685756555674, -59.94140625000001),
	new L.LatLng(16.678293098288528, -58.53515625),
	new L.LatLng(7.841615185204699, -42.0556640625),
	new L.LatLng(-32.175612478499325, 43.41796875),
	new L.LatLng(40.64730356252251, -22.7197265625),
	new L.LatLng(26.745610382199022, -43.9892578125),
	new L.LatLng(15.474857402687254, -60.24902343750001),
	new L.LatLng(-3.90809888189411, -3.1640625),
	new L.LatLng(10.714586690981509, -27.861328125),
	new L.LatLng(11.78132529611229, -57.76611328124999),
	new L.LatLng(31.5504526754715, -79.552001953125),
	new L.LatLng(25.443274612305746, -55.74462890625),
	new L.LatLng(36.421282443649496, -73.27880859375001),
	new L.LatLng(40.59727063442027, -68.8623046875),
	new L.LatLng(6.533645130567532, -31.9482421875),
	new L.LatLng(13.453737213419249, -70.400390625),
	new L.LatLng(16.035254862350413, -60.42480468750001),
	new L.LatLng(7.493196470122287, -54.40429687500001),
	new L.LatLng(36.87962060502676, -62.13867187499999),
	new L.LatLng(38.976492485539424, -65.14892578125),
	new L.LatLng(11.90497859698767, -73.509521484375),
	new L.LatLng(30.12612436422458, -69.10400390625),
	new L.LatLng(32.54681317351514, -64.2919921875),
	new L.LatLng(11.630715737981498, -60.86425781250001),
	new L.LatLng(27.644606381943326, -88.02246093750001),
	new L.LatLng(24.131715162462964, -83.46313476562499),
	new L.LatLng(19.103648251663646, -75.794677734375),
	new L.LatLng(17.680661583736246, -68.917236328125),
	new L.LatLng(39.26628442213066, -12.6123046875),
	new L.LatLng(25.780107118422244, -60.66650390624999),
	new L.LatLng(-6.315298538330033, 45.17578125),
	new L.LatLng(16.951724234434437, -60.69946289062501),
	new L.LatLng(23.115101554603044, -79.2498779296875),
	new L.LatLng(16.29905101458183, -41.044921875),
	new L.LatLng(-8.233237111274553, -23.6865234375),
	new L.LatLng(11.646856393732376, -68.2470703125),
	new L.LatLng(-1.7685179387242953, -10.360107421875),
	new L.LatLng(6.0968598188879355, -23.3349609375),
	new L.LatLng(11.501556900932487, -52.22900390625),
	new L.LatLng(0.5712795966325522, -14.0625),
	new L.LatLng(5.441022303717974, -50.185546875),
	new L.LatLng(17.560246503294913, -48.47167968749999),
	new L.LatLng(6.489983332670651, -52.25097656250001),
	new L.LatLng(0.39550467153201946, -21.181640624999996),
	new L.LatLng(5.397273407690917, -36.5625),
	new L.LatLng(10.098670120603392, -45.703125),
	new L.LatLng(17.926475979176452, -62.02880859375001),
	new L.LatLng(10.671404468527449, -53.34960937500001),
	new L.LatLng(-4.784468966579375, 1.7358398437499998),
	new L.LatLng(22.238259929564308, -82.5347900390625),
	new L.LatLng(37.61423141542417, -37.265625),
	new L.LatLng(21.417276156993662, -81.837158203125),
	new L.LatLng(22.978623970384913, -52.20703125),
	new L.LatLng(24.352101162808903, -81.9854736328125),
	new L.LatLng(16.53089842368169, -60.54565429687501),
	new L.LatLng(13.14367777049247, -63.65478515625),
	new L.LatLng(11.199956869621824, -59.55688476562501),
	new L.LatLng(-11.43695521614319, 49.1912841796875),
	new L.LatLng(-10.822515257716768, 44.439697265625),
	new L.LatLng(-9.199715262283302, 12.579345703125),
	new L.LatLng(-38.685509760012, 13.271484375),
	new L.LatLng(-25.90864446329127, 34.837646484375),
	new L.LatLng(-38.20365531807149, 29.70703125),
	new L.LatLng(-2.515061053188806, -1.549072265625),
	new L.LatLng(3.425691524418062, -2.3071289062500004),
	new L.LatLng(3.381823735328289, -1.2963867187500002),
	new L.LatLng(0.03845214555104571, 0.10986328125),
	new L.LatLng(-12.37219737335794, 40.748291015625),
	new L.LatLng(17.769612247142653, -17.775878906250004),
	new L.LatLng(-21.08450008351734, 57.6837158203125),
	new L.LatLng(-22.63429269379352, 54.3603515625),
	new L.LatLng(-20.879342971957897, 42.2314453125),
	new L.LatLng(-8.68963906812765, 39.5947265625),
	new L.LatLng(-6.271618064314864, 39.056396484375),
	new L.LatLng(-24.287026865376422, 41.484375),
	new L.LatLng(13.068776734357694, -18.281250000000004),
	new L.LatLng(16.135538853953427, -22.994384765624996),
	new L.LatLng(16.193574826697848, -18.940429687500004),
	new L.LatLng(-23.594194326203823, 35.7659912109375),
	new L.LatLng(10.439195529932327, -23.5052490234375),
	new L.LatLng(-9.297306856327584, 41.06689453125),
	new L.LatLng(-13.549881446917126, 41.72607421875),
	new L.LatLng(-15.188783763403254, 41.37451171875),
	new L.LatLng(-18.083200903334312, 39.7979736328125),
	new L.LatLng(-13.784736549340208, 45.69213867187499),
	new L.LatLng(-20.5144994821505, 57.72766113281249),
	new L.LatLng(-21.074248926792798, 56.44775390625),
	new L.LatLng(-20.385825381874263, 56.3983154296875),
	new L.LatLng(-21.156238366109417, 57.293701171875),
	new L.LatLng(4.171115454867424, 2.0434570312500004),
	new L.LatLng(2.789424777005989, -1.8017578125000002),
	new L.LatLng(1.5818302639606454, 7.371826171874999),
	new L.LatLng(4.302591077119676, 3.0102539062500004),
	new L.LatLng(-10.757762756247036, 12.0465087890625),
	new L.LatLng(-7.906911616469297, 10.458984375),
	new L.LatLng(3.5846952187809253, 4.757080078125),
	new L.LatLng(3.7162636347405162, 7.662963867187501),
	new L.LatLng(0.8239462091017685, 6.119384765625),
	new L.LatLng(-3.7217452310689536, 9.3548583984375),
	new L.LatLng(-34.03445260967645, 18.204345703125),
	new L.LatLng(5.747174076651375, -12.0849609375),
	new L.LatLng(6.206090498573885, -12.458496093750002),
	new L.LatLng(7.122696277518295, -13.666992187500002),
	new L.LatLng(26.745610382199022, -20.7421875),
	new L.LatLng(32.48196313217176, -16.7431640625),
	new L.LatLng(15.749962572748768, -20.2587890625),
	new L.LatLng(12.254127737657381, -19.2041015625),
	new L.LatLng(36.659606226479696, -9.20654296875),
	new L.LatLng(48.28319289548349, -6.15234375),
	new L.LatLng(42.19596877629178, -8.942871093749998),
	new L.LatLng(8.928487062665504, -15.930175781250002),
	new L.LatLng(0.14282211771738432, 6.899414062500001),
	new L.LatLng(-34.78673916270252, -57.67822265625),
	new L.LatLng(-30.38235321766958, -49.55932617187499),
	new L.LatLng(-26.22444694563432, -47.70263671875),
	new L.LatLng(-24.472150437226865, -45),
	new L.LatLng(-23.644524198573677, -42.4951171875),
	new L.LatLng(-22.973566591155144, -41.46240234375),
	new L.LatLng(-6.287998672327658, -34.71130371093749),
	new L.LatLng(-9.633245727691197, -35.474853515625),
	new L.LatLng(-16.573022719182777, -38.902587890625),
	new L.LatLng(-13.111580118251636, -38.408203125),
	new L.LatLng(11.598431619860792, -64.05029296875001),
	new L.LatLng(11.361567960696178, -62.29248046875001),
	new L.LatLng(10.13111684154069, -76.728515625),
	new L.LatLng(13.944729974920167, -82.81494140625001),
	new L.LatLng(16.351767849269347, -83.14453125),
	new L.LatLng(17.863747084405233, -85.3472900390625),
	new L.LatLng(20.838277806058933, -93.779296875),
	new L.LatLng(22.29926149974121, -90.802001953125),
	new L.LatLng(21.43261686447735, -85.462646484375),
	new L.LatLng(22.831883254915766, -84.63317871093749),
	new L.LatLng(29.511330027309146, -87.9345703125),
	new L.LatLng(28.8831596093235, -91.900634765625),
	new L.LatLng(23.347299312167785, -82.8314208984375),
	new L.LatLng(21.422389905231366, -79.9310302734375),
	new L.LatLng(21.130621534363144, -83.07861328125),
	new L.LatLng(23.392681978613, -80.57922363281249),
	new L.LatLng(16.404470456702423, -87.802734375),
	new L.LatLng(25.567220388070048, -78.22265625),
	new L.LatLng(25.48295117535531, -86.737060546875),
	new L.LatLng(-12.329269107612815, 54.656982421875),
	new L.LatLng(21.309846141087203, -75.83862304687499),
	new L.LatLng(22.014360653103207, -77.18994140625),
	new L.LatLng(20.24158281954221, -73.25683593750001),
	new L.LatLng(18.71909713096967, -77.486572265625),
	new L.LatLng(17.528820674552627, -77.84912109375),
	new L.LatLng(18.020527657852337, -75.93750000000001),
	new L.LatLng(19.228176737766262, -73.87207031250001),
	new L.LatLng(17.28770905062194, -76.387939453125),
	new L.LatLng(18.646245142670608, -68.00537109375),
	new L.LatLng(19.176301302579176, -68.741455078125),
	new L.LatLng(24.382124181118236, -85.858154296875),
	new L.LatLng(36.8092847020594, -75.45410156250001),
	new L.LatLng(38.58252615935333, -74.68505859375001),
	new L.LatLng(40.896905775860006, -71.707763671875),
	new L.LatLng(42.52069952914966, -70.048828125),
	new L.LatLng(-21.28937435586041, 50.537109375),
	new L.LatLng(26.03704188651584, -58.33740234375),
	new L.LatLng(24.246964554300938, -71.85058593750001),
	new L.LatLng(21.248422235627014, -74.8388671875),
	new L.LatLng(19.673625561844393, -76.5087890625),
	new L.LatLng(17.685895196738677, -76.827392578125),
	new L.LatLng(19.590844152960933, -77.904052734375),
	new L.LatLng(20.257043804632385, -77.7008056640625),
	new L.LatLng(33.32134852669881, -42.099609375),
	new L.LatLng(-13.496472765758952, -14.23828125),
	new L.LatLng(-24.766784522874428, -10.458984375),
	new L.LatLng(-33.504759069226075, -0.703125),
];
var links = [
	{ start: 0, end: 2 },
	{ start: 1, end: 2 },
	{ start: 2, end: 19 },
	{ start: 19, end: 4 },
	{ start: 4, end: 7 },
	{ start: 7, end: 6 },
	{ start: 6, end: 12 },
	{ start: 12, end: 11 },
	{ start: 11, end: 10 },
	{ start: 10, end: 9 },
	{ start: 9, end: 8 },
	{ start: 8, end: 5 },
	{ start: 11, end: 15 },
	{ start: 13, end: 14 },
	{ start: 14, end: 15 },
	{ start: 15, end: 20 },
	{ start: 20, end: 23 },
	{ start: 3, end: 77 },
	{ start: 17, end: 80 },
	{ start: 89, end: 15 },
	{ start: 48, end: 20 },
	{ start: 77, end: 23 },
	{ start: 23, end: 22 },
	{ start: 22, end: 29 },
	{ start: 29, end: 32 },
	{ start: 22, end: 75 },
	{ start: 75, end: 26 },
	{ start: 26, end: 31 },
	{ start: 22, end: 33 },
	{ start: 33, end: 34 },
	{ start: 34, end: 35 },
	{ start: 34, end: 37 },
	{ start: 37, end: 38 },
	{ start: 38, end: 39 },
	{ start: 35, end: 36 },
	{ start: 22, end: 21 },
	{ start: 21, end: 27 },
	{ start: 27, end: 85 },
	{ start: 80, end: 84 },
	{ start: 84, end: 27 },
	{ start: 27, end: 40 },
	{ start: 28, end: 25 },
	{ start: 25, end: 27 },
	{ start: 27, end: 55 },
	{ start: 24, end: 78 },
	{ start: 78, end: 27 },
	{ start: 55, end: 49 },
	{ start: 85, end: 74 },
	{ start: 74, end: 46 },
	{ start: 45, end: 69 },
	{ start: 85, end: 43 },
	{ start: 43, end: 81 },
	{ start: 43, end: 83 },
	{ start: 43, end: 58 },
	{ start: 43, end: 86 },
	{ start: 86, end: 79 },
	{ start: 86, end: 82 },
	{ start: 79, end: 50 },
	{ start: 82, end: 93 },
	{ start: 50, end: 96 },
	{ start: 96, end: 68 },
	{ start: 96, end: 56 },
	{ start: 56, end: 61 },
	{ start: 96, end: 76 },
	{ start: 50, end: 64 },
	{ start: 50, end: 97 },
	{ start: 50, end: 79 },
	{ start: 42, end: 57 },
	{ start: 42, end: 47 },
	{ start: 42, end: 41 },
	{ start: 93, end: 52 },
	{ start: 70, end: 66 },
	{ start: 52, end: 62 },
	{ start: 62, end: 51 },
	{ start: 52, end: 63 },
	{ start: 63, end: 53 },
	{ start: 63, end: 53 },
	{ start: 52, end: 59 },
	{ start: 91, end: 45 },
	{ start: 99, end: 98 },
	{ start: 111, end: 1 },
	{ start: 115, end: 1 },
	{ start: 102, end: 119 },
	{ start: 119, end: 0 },
	{ start: 113, end: 121 },
	{ start: 121, end: 122 },
	{ start: 108, end: 122 },
	{ start: 122, end: 123 },
	{ start: 123, end: 124 },
	{ start: 124, end: 0 },
	{ start: 125, end: 98 },
	{ start: 110, end: 126 },
	{ start: 111, end: 127 },
	{ start: 98, end: 128 },
	{ start: 128, end: 129 },
	{ start: 129, end: 110 },
	{ start: 123, end: 112 },
	{ start: 112, end: 115 },
	{ start: 16, end: 132 },
	{ start: 131, end: 16 },
	{ start: 130, end: 16 },
	{ start: 133, end: 16 },
	{ start: 134, end: 13 },
	{ start: 135, end: 13 },
	{ start: 136, end: 16 },
	{ start: 137, end: 136 },
	{ start: 138, end: 16 },
	{ start: 139, end: 18 },
	{ start: 18, end: 16 },
	{ start: 134, end: 7 },
	{ start: 19, end: 140 },
	{ start: 141, end: 28 },
	{ start: 142, end: 28 },
	{ start: 143, end: 28 },
	{ start: 69, end: 144 },
	{ start: 146, end: 147 },
	{ start: 147, end: 24 },
	{ start: 144, end: 146 },
	{ start: 145, end: 146 },
	{ start: 69, end: 149 },
	{ start: 69, end: 148 },
	{ start: 69, end: 150 },
	{ start: 151, end: 24 },
	{ start: 132, end: 152 },
	{ start: 152, end: 18 },
	{ start: 18, end: 139 },
	{ start: 139, end: 135 },
	{ start: 135, end: 134 },
	{ start: 100, end: 134 },
	{ start: 134, end: 100 },
	{ start: 135, end: 100 },
	{ start: 100, end: 135 },
	{ start: 135, end: 18 },
	{ start: 140, end: 19 },
	{ start: 1, end: 115 },
	{ start: 7, end: 134 },
	{ start: 16, end: 131 },
	{ start: 16, end: 104 },
	{ start: 104, end: 48 },
	{ start: 16, end: 107 },
	{ start: 117, end: 146 },
	{ start: 116, end: 147 },
	{ start: 17, end: 28 },
	{ start: 28, end: 24 },
	{ start: 24, end: 147 },
	{ start: 147, end: 146 },
	{ start: 24, end: 78 },
	{ start: 142, end: 28 },
	{ start: 143, end: 28 },
	{ start: 146, end: 118 },
	{ start: 117, end: 146 },
	{ start: 146, end: 147 },
	{ start: 147, end: 24 },
	{ start: 24, end: 78 },
	{ start: 78, end: 27 },
	{ start: 28, end: 17 },
	{ start: 17, end: 3 },
	{ start: 17, end: 131 },
	{ start: 143, end: 28 },
	{ start: 30, end: 28 },
	{ start: 105, end: 131 },
	{ start: 106, end: 131 },
	{ start: 106, end: 131 },
	{ start: 131, end: 106 },
	{ start: 141, end: 28 },
	{ start: 28, end: 141 },
	{ start: 28, end: 143 },
	{ start: 118, end: 146 },
	{ start: 109, end: 118 },
	{ start: 120, end: 30 },
	{ start: 49, end: 120 },
	{ start: 114, end: 121 },
	{ start: 123, end: 125 },
	{ start: 108, end: 99 },
	{ start: 18, end: 89 },
	{ start: 39, end: 153 },
	{ start: 36, end: 155 },
	{ start: 36, end: 157 },
	{ start: 36, end: 156 },
	{ start: 36, end: 154 },
	{ start: 157, end: 158 },
	{ start: 32, end: 159 },
	{ start: 32, end: 160 },
	{ start: 31, end: 161 },
	{ start: 31, end: 162 },
	{ start: 64, end: 164 },
	{ start: 96, end: 163 },
	{ start: 61, end: 165 },
	{ start: 165, end: 166 },
	{ start: 166, end: 165 },
	{ start: 166, end: 167 },
	{ start: 167, end: 168 },
	{ start: 168, end: 171 },
	{ start: 171, end: 170 },
	{ start: 170, end: 169 },
	{ start: 169, end: 170 },
	{ start: 170, end: 171 },
	{ start: 171, end: 168 },
	{ start: 168, end: 167 },
	{ start: 167, end: 166 },
	{ start: 65, end: 173 },
	{ start: 65, end: 174 },
	{ start: 73, end: 178 },
	{ start: 178, end: 175 },
	{ start: 175, end: 172 },
	{ start: 172, end: 171 },
	{ start: 171, end: 172 },
	{ start: 172, end: 175 },
	{ start: 171, end: 177 },
	{ start: 168, end: 179 },
	{ start: 73, end: 180 },
	{ start: 181, end: 65 },
	{ start: 185, end: 67 },
	{ start: 185, end: 67 },
	{ start: 67, end: 186 },
	{ start: 185, end: 189 },
	{ start: 188, end: 190 },
	{ start: 190, end: 187 },
	{ start: 68, end: 191 },
	{ start: 191, end: 192 },
	{ start: 66, end: 193 },
	{ start: 193, end: 181 },
	{ start: 53, end: 194 },
	{ start: 53, end: 195 },
	{ start: 54, end: 197 },
	{ start: 54, end: 196 },
	{ start: 52, end: 199 },
	{ start: 199, end: 70 },
	{ start: 185, end: 201 },
	{ start: 201, end: 183 },
	{ start: 67, end: 202 },
	{ start: 67, end: 186 },
	{ start: 67, end: 188 },
	{ start: 190, end: 203 },
	{ start: 202, end: 204 },
	{ start: 204, end: 205 },
	{ start: 177, end: 92 },
	{ start: 92, end: 176 },
	{ start: 92, end: 90 },
	{ start: 175, end: 94 },
	{ start: 59, end: 60 },
	{ start: 60, end: 54 },
	{ start: 79, end: 42 },
	{ start: 42, end: 95 },
	{ start: 42, end: 72 },
	{ start: 42, end: 87 },
	{ start: 46, end: 206 },
	{ start: 206, end: 91 },
	{ start: 23, end: 207 },
	{ start: 207, end: 208 },
	{ start: 208, end: 209 },
	{ start: 209, end: 101 },
	{ start: 101, end: 103 },
	{ start: 103, end: 44 },
	{ start: 44, end: 198 },
	{ start: 198, end: 182 },
	{ start: 182, end: 71 },
	{ start: 44, end: 1 },
	{ start: 44, end: 111 },
	{ start: 70, end: 200 },
	{ start: 200, end: 73 },
	{ start: 200, end: 184 },
	{ start: 70, end: 185 },
];