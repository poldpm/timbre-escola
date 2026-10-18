#!/bin/bash
# Proves bàsiques de l'API contra el servidor demo (bash tools/demo.sh en una altra terminal).
# Si la contrasenya encara no està configurada, la configura com "escorial".
U=${U:-http://localhost:8099}
CK=$(mktemp); C="curl -s -c $CK -b $CK"; J='-H Content-Type:application/json'

$C -X POST $J -d '{"contrasenya":"escorial"}' $U/api/configura >/dev/null
$C -X POST $J -d '{"contrasenya":"escorial"}' $U/api/login; echo

echo "--- sense login ha de donar 401:"; curl -s -o /dev/null -w "%{http_code}\n" $U/api/estat
echo "--- hora invàlida ha de donar error:"; $C -X PATCH $J -d '{"tocs":[{"hora":"25:00","durada":60,"dies":[0]}]}' $U/api/config; echo
echo "--- path traversal ha de donar 404:"; $C -o /dev/null -w "%{http_code}\n" "$U/api/cancons/..%2Fconfig.json/audio"

sel(){ $C $U/api/estat | python3 -c "import json,sys; print('   ', json.load(sys.stdin)['seleccio'])"; }
toca(){ $C -X POST $J -d '{"segons":5}' $U/api/toca | python3 -c "import json,sys; print('    toca:', json.load(sys.stdin).get('canco'))"; }

echo "--- mode cada_toc (han de ser diferents):"
$C -X PATCH $J -d '{"seleccio":{"mode":"cada_toc"}}' $U/api/config >/dev/null; toca; toca; toca
echo "--- mode dia (ha de ser sempre la mateixa):"
$C -X PATCH $J -d '{"seleccio":{"mode":"dia"}}' $U/api/config >/dev/null; sel; toca; toca
echo "--- canvia la del dia:"; $C -X POST $J -d '{}' $U/api/periode; echo
echo "--- mode setmana:"; $C -X PATCH $J -d '{"seleccio":{"mode":"setmana"}}' $U/api/config >/dev/null; sel
echo "--- fixa sense cançó ha de donar error:"; $C -X PATCH $J -d '{"seleccio":{"mode":"fixa"}}' $U/api/config; echo
echo "--- tornem a cada_toc"; $C -X PATCH $J -d '{"seleccio":{"mode":"cada_toc"}}' $U/api/config >/dev/null; sel
rm -f $CK
