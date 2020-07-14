"""cat4k implementation of show_platform.py

"""
import re

from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional


class ShowModuleSchema(MetaParser):
    """Schema for show module"""
    schema = {
        'chassis_type': str,
        'power_consumed': str,
        'mod': {
            Any(): {
                'port': int,
                'card_type': str,
                'model': str,
                'serial_number': str,
                'mac_address_from': str,
                'mac_address_to': str,
                'hw_ver': str,
                Optional('fw_ver'): str,
                Optional('sw_ver'): str,
                'status': str,
                Optional('redundancy_role'): str,
                Optional('operating_mode'): str,
                Optional('redundancy_status'): str
            }
        },
        'system_failures': {
            'power_supply': str
        }
    }


class ShowModule(ShowModuleSchema):
    """Parser for show module"""
    cli_command = 'show module'

    def cli(self,output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        ret_dict = {}

        # Chassis Type : WS-C4507R+E
        p1 = re.compile(r'^Chassis Type +: +(?P<chassis_type>.+)$')

        # Power consumed by backplane : 40 Watts
        p2 = re.compile(r'^Power consumed by backplane +: +(?P<power_consumed>.+)$')

        # 1    48  10/100/1000BaseT Premium POE E Series  WS-X4648-RJ45V+E   ABCDE123456
        # 3     6  Sup 7L-E 10GE (SFP+), 1000BaseX (SFP)  WS-X45-SUP7L-E     QWERT987654
        p3 = re.compile(r'^(?P<mod>\d+) +(?P<port>\d+) +(?P<card_type>[\S\s]+) +(?P<model>\S+) +(?P<serial_number>\S+)$')

        # 3 555a.88ff.584c to 555a.88ff.5859 3.0 15.0(1r)SG10 03.06.07.E       Ok
        p4 = re.compile(r'^(?P<mod>\d+) +(?P<mac_address_from>[\w\.]+) +to +(?P<mac_address_to>[\w\.]+) +(?P<hw_ver>[\w\.\(\)]+) +(?P<fw_ver>[\w\.\(\)]+) +(?P<sw_ver>[\w\.\(\)]+) +(?P<status>\w+)$')

        # 1 11a1.b2ff.ee55 to 11a1.b2ff.ee61 3.1                               Ok
        p4_1 = re.compile(r'^(?P<mod>\d+) +(?P<mac_address_from>[\w\.]+) +to +(?P<mac_address_to>[\w\.]+) +(?P<hw_ver>[\w\.\(\)]+) +(?P<status>\w+)$')
        
        # 3   Active Supervisor   RPR                 Active
        p5 = re.compile(r'^(?P<mod>\d+) +(?P<redundancy_role>[\S\s]+) +(?P<operating_mode>\S+) +(?P<redundancy_status>\S+)$')

        # Power Supply:   bad/off (see 'show power')
        p6 = re.compile(r'^Power Supply: +(?P<power_supply>.+)$')


        for line in out.splitlines():
            line = line.strip()

            # Chassis Type : WS-C4507R+E
            m = p1.match(line)
            if m:
                group = m.groupdict()
                ret_dict.update({'chassis_type': group['chassis_type']})
                continue
                
            # Power consumed by backplane : 40 Watts
            m = p2.match(line)
            if m:
                group = m.groupdict()
                ret_dict.update({'power_consumed': group['power_consumed']})
                continue

            # 1    48  10/100/1000BaseT Premium POE E Series  WS-X4648-RJ45V+E   ABCDE123456
            # 3     6  Sup 7L-E 10GE (SFP+), 1000BaseX (SFP)  WS-X45-SUP7L-E     QWERT987654
            m = p3.match(line)
            if m:
                group = m.groupdict()
                mode_dict = ret_dict.setdefault('mod', {}).setdefault(int(group['mod']), {})
                mode_dict.update({'port': int(group['port'])})
                mode_dict.update({'card_type': group['card_type'].strip()})
                mode_dict.update({'model': group['model']})
                mode_dict.update({'serial_number': group['serial_number']})
                continue

            # 3 555a.88ff.584c to 555a.88ff.5859 3.0 15.0(1r)SG10 03.06.07.E       Ok
            m = p4.match(line)
            if m:
                group = m.groupdict()
                mode_dict = ret_dict.setdefault('mod', {}).setdefault(int(group['mod']), {})
                mode_dict.update({'mac_address_from': group['mac_address_from']})
                mode_dict.update({'mac_address_to': group['mac_address_to']})
                mode_dict.update({'hw_ver': group['hw_ver']})
                mode_dict.update({'fw_ver': group['fw_ver']})
                mode_dict.update({'sw_ver': group['sw_ver']})
                mode_dict.update({'status': group['status']})
                continue

            # 1 11a1.b2ff.ee55 to 11a1.b2ff.ee61 3.1                               Ok
            m = p4_1.match(line)
            if m:
                group = m.groupdict()
                mode_dict = ret_dict.setdefault('mod', {}).setdefault(int(group['mod']), {})
                mode_dict.update({'mac_address_from': group['mac_address_from']})
                mode_dict.update({'mac_address_to': group['mac_address_to']})
                mode_dict.update({'hw_ver': group['hw_ver']})
                mode_dict.update({'status': group['status']})
                continue

            # 3   Active Supervisor   RPR                 Active
            m = p5.match(line)
            if m:
                group = m.groupdict()
                mode_dict = ret_dict.setdefault('mod', {}).setdefault(int(group['mod']), {})
                mode_dict.update({'redundancy_role': group['redundancy_role'].strip()})
                mode_dict.update({'operating_mode': group['operating_mode']})
                mode_dict.update({'redundancy_status': group['redundancy_status']})
                continue

            ## Power Supply:   bad/off (see 'show power')
            m = p6.match(line)
            if m:
                group = m.groupdict()
                system_dict = ret_dict.setdefault('system_failures', {})
                system_dict.update({'power_supply': group['power_supply']})
                continue

        return ret_dict


    # =====================
# Schema for:
#   * 'show inventory'
# =====================
class ShowInventorySchema(MetaParser):

    ''' Schema for:
        * 'show inventory'
    '''

    schema = {
        Optional('main'):
            {Optional('swstack'): bool,
             Optional('chassis'):
                {Any():
                    {Optional('name'): str,
                     Optional('descr'): str,
                     Optional('pid'): str,
                     Optional('vid'): str,
                     Optional('sn'): str,
                     },
                 },
             },
        Optional('slot'):
            {Any():
                {Optional('rp'):
                    {Any():
                        {Optional('name'): str,
                         Optional('descr'): str,
                         Optional('pid'): str,
                         Optional('vid'): str,
                         Optional('sn'): str,
                         Optional('swstack_power'): str,
                         Optional('swstack_power_sn'): str,
                         Optional('subslot'):
                            {Any():
                                {Any():
                                    {Optional('name'): str,
                                     Optional('descr'): str,
                                     Optional('pid'): str,
                                     Optional('vid'): str,
                                     Optional('sn'): str,
                                     },
                                 },
                             },
                         },
                     },
                 Optional('lc'):
                    {Any():
                        {Optional('name'): str,
                         Optional('descr'): str,
                         Optional('pid'): str,
                         Optional('vid'): str,
                         Optional('sn'): str,
                         Optional('swstack_power'): str,
                         Optional('swstack_power_sn'): str,
                         Optional('subslot'):
                            {Any():
                                {Any():
                                    {Optional('name'): str,
                                     Optional('descr'): str,
                                     Optional('pid'): str,
                                     Optional('vid'): str,
                                     Optional('sn'): str,
                                     },
                                 },
                             },
                         },
                     },
                 Optional('other'):
                    {Any():
                        {Optional('name'): str,
                         Optional('descr'): str,
                         Optional('pid'): str,
                         Optional('vid'): str,
                         Optional('sn'): str,
                         Optional('swstack_power'): str,
                         Optional('swstack_power_sn'): str,
                         Optional('subslot'):
                            {Any():
                                {Any():
                                    {Optional('name'): str,
                                     Optional('descr'): str,
                                     Optional('pid'): str,
                                     Optional('vid'): str,
                                     Optional('sn'): str,
                                     },
                                 },
                             },
                         },
                     },
                 },
             },
    }


# ====================
# Parser for:
#   * 'show inventory'
# ====================
class ShowInventory(ShowInventorySchema):

    ''' Parser for:
        * 'show inventory'
    '''

    cli_command = ['show inventory']

    def cli(self, output=None):

        if output is None:
            # Build command
            cmd = self.cli_command[0]
            # Execute command
            out = self.device.execute(cmd)
        else:
            out = output

        # Init vars
        ret_dict = {}
        name = descr = slot = subslot = pid = ''
        asr900_rp = False

        # NAME: "Switch 1", DESCR: "WS-C3850-24P-E"
        # NAME: "StackPort5/2", DESCR: "StackPort5/2"
        # NAME: "Switch 5 - Power Supply A", DESCR: "Switch 5 - Power Supply A"
        # NAME: "subslot 0/0 transceiver 2", DESCR: "GE T"
        # NAME: "NIM subslot 0/0", DESCR: "Front Panel 3 ports Gigabitethernet Module"
        # NAME: "Modem 0 on Cellular0/2/0", DESCR: "Sierra Wireless EM7455/EM7430"
        p1 = re.compile(r'^NAME: +\"(?P<name>.*)\",'
                        r' +DESCR: +\"(?P<descr>.*)\"$')

        # Switch 1
        # module 0
        #p1_1 = re.compile(r'^(Switch|[Mm]odule) +(?P<slot>(\S+))')
        # try 1 p1_1 = re.compile(r'^(Switch|[Mm]odule)( *)+(?P<slot>(\S+))')
        p1_1 = re.compile(r'^(Switch|[Mm]odule) *(?P<slot>(\S+))')

        # Power Supply Module 0
        # Power Supply Module 1
        p1_2 = re.compile(r'Power Supply Module')

        # SPA subslot 0/0
        # IM subslot 0/1
        # NIM subslot 0/0
        p1_3 = re.compile(r'^(SPA|IM|NIM|PVDM) +subslot +(?P<slot>(\d+))/(?P<subslot>(\d+))')

        # subslot 0/0 transceiver 0
        p1_4 = re.compile(r'^subslot +(?P<slot>(\d+))\/(?P<subslot>(.*))')

        # StackPort1/1
        p1_5 = re.compile(r'^StackPort(?P<slot>(\d+))/(?P<subslot>(\d+))$')

        # Fan Tray
        p1_6 = re.compile(r'^Fan +Tray$')

        # Modem 0 on Cellular0/2/0
        p1_7 = re.compile(r'^Modem +(?P<modem>\S+) +on +Cellular(?P<slot>\d+)\/(?P<subslot>.*)$')

        # PID: ASR-920-24SZ-IM   , VID: V01  , SN: CAT1902V19M
        # PID: SFP-10G-LR        , VID: CSCO , SN: CD180456291
        # PID: A900-IMA3G-IMSG   , VID: V01  , SN: FOC2204PAP1
        # PID: SFP-GE-T          , VID: V02  , SN: MTC2139029X
        # PID: ISR4331-3x1GE     , VID: V01  , SN:
        # PID: ISR4331/K9        , VID:      , SN: FDO21520TGH
        # PID: ISR4331/K9        , VID:      , SN:
        # PID: , VID: 1.0  , SN: 1162722191
        p2 = re.compile(r'^PID: +(?P<pid>[\S\s]+)? *, +VID:(?: +(?P<vid>(\S+)))? *,'
                        r' +SN:(?: +(?P<sn>(\S+)))?$')

        for line in out.splitlines():
            line = line.strip()

            # NAME: "Switch 1", DESCR: "WS-C3850-24P-E"
            # NAME: "StackPort5/2", DESCR: "StackPort5/2"
            # NAME: "Switch 5 - Power Supply A", DESCR: "Switch 5 - Power Supply A"
            # NAME: "subslot 0/0 transceiver 2", DESCR: "GE T"
            # NAME: "NIM subslot 0/0", DESCR: "Front Panel 3 ports Gigabitethernet Module"
            # NAME: "Modem 0 on Cellular0/2/0", DESCR: "Sierra Wireless EM7455/EM7430"
            m = p1.match(line)
            if m:
                group = m.groupdict()
                name = group['name'].strip()
                descr = group['descr'].strip()

                # ------------------------------------------------------------------
                # Define slot_dict
                # ------------------------------------------------------------------
                m1_1 = p1_1.match(name)
                if m1_1:
                    slot = m1_1.groupdict()['slot']
                    # Creat slot_dict
                    slot_dict = ret_dict.setdefault('slot', {}).setdefault(slot, {})

                m1_2 = p1_2.match(name)
                if m1_2:
                    slot = name.replace('Power Supply Module ', 'P')
                    # Creat slot_dict
                    slot_dict = ret_dict.setdefault('slot', {}).setdefault(slot, {})

                # ------------------------------------------------------------------
                # Define subslot
                # ------------------------------------------------------------------
                m = p1_3.match(name) or p1_4.match(name) or p1_5.match(name) or p1_7.match(name)
                if m:
                    group = m.groupdict()
                    slot = group['slot']
                    subslot = group['subslot']
                    # Creat slot_dict
                    slot_dict = ret_dict.setdefault('slot', {}).setdefault(slot, {})

                m1_6 = p1_6.match(name)
                if m1_6:
                    slot = name.replace(' ', '_')
                    # Create slot_dict
                    slot_dict = ret_dict.setdefault('slot', {}).setdefault(slot, {})
                # go to next line
                continue

            # PID: ASR-920-24SZ-IM   , VID: V01  , SN: CAT1902V19M
            # PID: SFP-10G-LR        , VID: CSCO , SN: CD180456291
            # PID: A900-IMA3G-IMSG   , VID: V01  , SN: FOC2204PAP1
            # PID: SFP-GE-T          , VID: V02  , SN: MTC2139029X
            # PID: ISR4331-3x1GE     , VID: V01  , SN:
            # PID: ISR4331/K9        , VID:      , SN: FDO21520TGH
            # PID: ISR4331/K9        , VID:      , SN:
            # PID: EM7455/EM7430     , VID: 1.0  , SN: 355813070074072
            m = p2.match(line)
            if m:
                group = m.groupdict()
                if group.get('pid'):
                    pid = group['pid'].strip(' ')
                else:
                    pid = ''
                vid = group['vid'] or ''
                sn = group['sn'] or ''

                # NAME: "Chassis", DESCR: "Cisco ASR1006 Chassis"
                if 'Chassis' in name:
                    main_dict = ret_dict.setdefault('main', {}).\
                        setdefault('chassis', {}).\
                        setdefault(pid, {})
                    main_dict['name'] = name
                    main_dict['descr'] = descr
                    main_dict['pid'] = pid
                    main_dict['vid'] = vid
                    main_dict['sn'] = sn

                # PID: STACK-T1-50CM     , VID: V01  , SN: LCC1921G250
                if 'STACK' in pid:
                    main_dict = ret_dict.setdefault('main', {})
                    main_dict['swstack'] = True

                if ('ASR-9') in pid and ('PWR' not in pid) and ('FAN' not in pid):
                    rp_dict = ret_dict.setdefault('slot', {}).\
                        setdefault('0', {}).\
                        setdefault('rp', {}).\
                        setdefault(pid, {})
                    rp_dict['name'] = name
                    rp_dict['descr'] = descr
                    rp_dict['pid'] = pid
                    rp_dict['vid'] = vid
                    rp_dict['sn'] = sn
                    asr900_rp = True

                # Ensure name, slot have been previously parsed
                if not name or not slot:
                    continue

                # PID: ASR1000-RP2       , VID: V02  , SN: JAE153408NJ
                # PID: ASR1000-RP2       , VID: V03  , SN: JAE1703094H
                # PID: WS-C3850-24P-E    , VID: V01  , SN: FCW1932D0LB
                if ('RP' in pid) or ('WS-C' in pid) or ('R' in name):
                    rp_dict = slot_dict.setdefault('rp', {}).\
                        setdefault(pid, {})
                    rp_dict['name'] = name
                    rp_dict['descr'] = descr
                    rp_dict['pid'] = pid
                    rp_dict['vid'] = vid
                    rp_dict['sn'] = sn

                # PID: ASR1000-SIP40     , VID: V02  , SN: JAE200609WP
                # PID: ISR4331/K9        , VID:      , SN: FDO21520TGH
                # PID: ASR1002-X         , VID: V07, SN: FOX1111P1M1
                # PID: ASR1002-HX        , VID:      , SN:
                elif (('SIP' in pid)  or ('-X' in pid) or \
                     ('-HX' in pid) or ('module' in name and not ('module F' in name))) and \
                     ('subslot' not in name):

                    lc_dict = slot_dict.setdefault('lc', {}).\
                        setdefault(pid, {})
                    lc_dict['name'] = name
                    lc_dict['descr'] = descr
                    lc_dict['pid'] = pid
                    lc_dict['vid'] = vid
                    lc_dict['sn'] = sn

                # PID: SP7041-E          , VID: E    , SN: MTC164204VE
                # PID: SFP-GE-T          , VID: V02  , SN: MTC2139029X
                # PID: EM7455/EM7430     , VID: 1.0  , SN: 355813070074072
                elif subslot:
                    if ('STACK' in pid) or asr900_rp:
                        subslot_dict = rp_dict.setdefault('subslot', {}).\
                            setdefault(subslot, {}).\
                            setdefault(pid, {})
                    else:
                        if 'lc' not in slot_dict:
                            lc_dict = slot_dict.setdefault('lc', {}). \
                                setdefault(pid, {})
                        subslot_dict = lc_dict.setdefault('subslot', {}).\
                            setdefault(subslot, {}).\
                            setdefault(pid, {})
                    subslot_dict['name'] = name
                    subslot_dict['descr'] = descr
                    subslot_dict['pid'] = pid
                    subslot_dict['vid'] = vid
                    subslot_dict['sn'] = sn

                # PID: ASR1006-PWR-AC    , VID: V01  , SN: ART1210Q049
                # PID: ASR1006-PWR-AC    , VID: V01  , SN: ART1210Q04C
                # PID: ASR-920-FAN-M     , VID: V01  , SN: CAT1903V028
                else:
                    other_dict = slot_dict.setdefault('other', {}).\
                        setdefault(pid, {})
                    other_dict['name'] = name
                    other_dict['descr'] = descr
                    other_dict['pid'] = pid
                    other_dict['vid'] = vid
                    other_dict['sn'] = sn

                # Reset to avoid overwrite
                name = descr = slot = subslot = ''
                continue

        return ret_dict

