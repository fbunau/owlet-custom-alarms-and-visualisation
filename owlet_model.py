import re

def clean_data(data):
  bpm_insensitive = re.compile(re.escape("bpm"), re.IGNORECASE)
  bpn_insensitive = re.compile(re.escape("bpn"), re.IGNORECASE)
  if data["bpm"] is not None:
    parsed = bpm_insensitive.sub("", bpn_insensitive.sub("", data["bpm"])).strip()
    data["bpm"] = int(parsed) if (parsed.isdigit()) else None
  if data["o2"] is not None:
    data["o2"] = 100 if (data["o2"][:3] == "100") else int(data["o2"][:2]) if (data["o2"][:2].isdigit()) else None
  if data["status"] is not None:
    data["status"] = data["status"].strip()
  return data
