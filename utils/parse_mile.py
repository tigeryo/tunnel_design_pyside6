import re
from decimal import Decimal, ROUND_DOWN


def mile_str2num(mile_str):
    pattern = re.compile(r'(.*)K(.*)\+(.*)', re.I)
    result = pattern.findall(mile_str.upper())

    assert len(result) == 1, f'mile: {mile_str} is not correct'
    result = result[0]

    return 1000 * int(result[1]) + float(result[2]), f'{result[0]}K'

def mile_num2str(mile_num, front_k='K', mode='full'):
    """convert mile number to string, e.g. 200.123456789 -> K200+123.456789000
    mile_num: float, like 200.123456789
    front_k: str endwith 'K', like 'K', 'ZK', 'D2K'
    mode: optional, 'full', 'simple' or 'short'
        'full': 200.123456789 -> K200+123.456789000
        'simple': 200.123456789 -> K200+123.457
        'short': 200.123456789 -> K200+123
    """
    # convert to decimal number
    value = Decimal(str(mile_num)).quantize(Decimal('1e-10'), rounding=ROUND_DOWN)

    # calculate km and m part
    km_part = (value // 1000).to_integral_value()
    meter_value = value % 1000

    # format km part
    km_str = f"{int(km_part):03d}"

    # format m part
    if meter_value == meter_value.to_integral_value():
        if mode in ['simple', 'full']:
            meter_str = f'{int(meter_value):03d}.000'
        else:
            meter_str = f"{int(meter_value):03d}"
    else:
        # split integer and decimal
        meter_str = format(meter_value.normalize(), 'f').rstrip('0').rstrip('.')
        int_part, _, dec_part = meter_str.partition('.')

        # integer part
        int_part = int_part.zfill(3)

        # combine
        if mode == 'full':
            meter_str = f"{int_part}.{dec_part}" if dec_part else int_part
        elif mode == 'simple':
            meter_str = f"{int_part}.{dec_part[:3]}" if dec_part else int_part
        else:
            meter_str = int_part

    return f"{front_k}{km_str}+{meter_str}"
