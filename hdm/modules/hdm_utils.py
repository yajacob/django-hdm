class HdmUtils(object):
    def model_str_clean(self, stype, mstr):
        result = ""
        if stype == "fa":
            # Pink, Blue, Yellow|16GB, 32GB, 64GB, 128GB|USPS, UPS, FedEx|
            for idx, grp in enumerate(mstr.split("|")):
                if len(grp) < 1:
                    continue
                if idx > 0:
                    result += "|"
                for idx2, item in enumerate(grp.split(",")):
                    if idx2 > 0:
                        result += ","
                    result += item.strip()
        # "cr" or "al"
        else:
            # Color, Memory, Delivery
            for idx, item in enumerate(mstr.split(",")):
                if len(item) < 1:
                    continue
                if idx > 0:
                    result += ","
                result += item.strip()
        return result
