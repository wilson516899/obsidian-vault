/**
 * budget_reader.mjs
 * Reads LightByte Budget app's Realm database and outputs JSON to stdout.
 * Called by budget_import.py via subprocess.
 *
 * Usage: node budget_reader.mjs <realm_file_path>
 */

import Realm from 'realm';
import path from 'path';

const realmPath = process.argv[2];
if (!realmPath) {
  process.stderr.write('Usage: node budget_reader.mjs <realm_file_path>\n');
  process.exit(1);
}

try {
  const realm = await Realm.open({
    path: realmPath,
    readOnly: true,
  });

  const records = realm.objects('Expend');
  const rows = [];

  for (let i = 0; i < records.length; i++) {
    const r = records[i];
    const row = {};

    // date (stored as Date object)
    try {
      row.date = r.date ? new Date(r.date).toISOString().split('T')[0] : null;
    } catch { row.date = null; }

    // classify (category) - linked Realm object
    try {
      const c = r.classify;
      row.classify = c ? (c.name || null) : null;
    } catch { row.classify = null; }

    // subcategory - linked Realm object
    try {
      const s = r.subcategory;
      row.subcategory = s ? (s.name || null) : null;
    } catch { row.subcategory = null; }

    // isIncome
    try { row.isIncome = r.isIncome ?? false; } catch { row.isIncome = false; }

    // amount (in account currency)
    try { row.amount = r.amount ?? 0; } catch { row.amount = 0; }

    // originalCost (in original currency)
    try { row.originalCost = r.originalCost ?? 0; } catch { row.originalCost = 0; }

    // originalCurrency
    try { row.currency = r.originalCurrency || 'TWD'; } catch { row.currency = 'TWD'; }

    // remark / notes
    try { row.remark = r.remark || null; } catch { row.remark = null; }

    rows.push(row);
  }

  realm.close();
  process.stdout.write(JSON.stringify(rows, null, 2));
  process.exit(0);

} catch (err) {
  process.stderr.write(`Error: ${err.message}\n`);
  process.exit(1);
}
