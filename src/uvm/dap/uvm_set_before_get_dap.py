#//
#//----------------------------------------------------------------------------
#//   Copyright 2007-2011 Mentor Graphics Corporation
#//   Copyright 2007-2011 Cadence Design Systems, Inc.
#//   Copyright 2010-2011 Synopsys, Inc.
#//   Copyright 2013      NVIDIA Corporation
#//   Copyright 2019      Tuomas Poikela (tpoikela)
#//   All Rights Reserved Worldwide
#//
#//   Licensed under the Apache License, Version 2.0 (the
#//   "License"); you may not use this file except in
#//   compliance with the License.  You may obtain a copy of
#//   the License at
#//
#//       http://www.apache.org/licenses/LICENSE-2.0
#//
#//   Unless required by applicable law or agreed to in
#//   writing, software distributed under the License is
#//   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#//   CONDITIONS OF ANY KIND, either express or implied.  See
#//   the License for the specific language governing
#//   permissions and limitations under the License.
#//----------------------------------------------------------------------------
#

from .uvm_set_get_dap_base import uvm_set_get_dap_base
from ..macros.uvm_object_defines import uvm_object_utils
from ..macros.uvm_message_defines import *
from ..base.sv import sv
from ..base.uvm_globals import uvm_check_output_args

ERR_MSG1 = "Attempt to get value on '%s', but the data access policy forbits calling 'get' prior to calling 'set' or 'try_set'!"

#// Class: uvm_set_before_get_dap
#// Provides a 'Set Before Get' Data Access Policy.
#//
#// The 'Set Before Get' Data Access Policy enforces that the value must
#// be written at ~least~ once before it is read.  This DAP can be used to
#// pass shared information to multiple components during standard configuration,
#// even if that information hasn't yet been determined.
#//
#// Such DAP objects can be useful for passing a 'placeholder' reference, before
#// the information is actually available.  A good example of this would be
#// the virtual sequencer:
#//
#//| typedef uvm_set_before_get_dap#(uvm_sequencer_base) seqr_dap_t;
#//| virtual_seqeuncer_type virtual_sequencer;
#//| agent_type my_agent;
#//| seqr_dap_t seqr_dap;
#//|
#//| function void my_env::build_phase(uvm_phase phase);
#//|   seqr_dap = seqr_dap_t::type_id::create("seqr_dap");
#//|   // Pass the DAP, because we don't have a reference to the
#//|   // real sequencer yet...
#//|   uvm_config_db#(seqr_dap_t)::set(this, "virtual_sequencer", "seqr_dap", seqr_dap);
#//|
#//|   // Create the virtual sequencer
#//|   virtual_sequencer = virtual_sequencer_type::type_id::create("virtual_sequencer", this);
#//|
#//|   // Create the agent
#//|   agent = agent_type::type_id::create("agent", this);
#//| endfunction
#//|
#//| function void my_env::connect_phase(uvm_phase phase);
#//|   // Now that we know the value is good, we can set it
#//|   seqr_dap.set(agent.sequencer);
#//| endfunction
#//
#// In the example above, the environment didn't have a reference to the
#// agent's sequencer yet, because the agent hadn't executed its ~build_phase~.
#// The environment needed to give the virtual sequencer a "Set before get" DAP
#// so that the virtual sequencer (and any sequences one it), could ~eventually~
#// see the agent's sequencer, when the reference was finally available.  If
#// the virtual sequencer (or any sequences on it) attempted to 'get' the
#// reference to the agent's sequencer ~prior~ to the environment assigning it,
#// an error would have been reported.
#
#class uvm_set_before_get_dap#(type T=int) extends uvm_set_get_dap_base#(T);
class uvm_set_before_get_dap(uvm_set_get_dap_base):
    #
    #   // Used for self-references
    #   typedef uvm_set_before_get_dap#(T) this_type;
    #
    #   // Function: new
    #   // Constructor
    def __init__(self, name="unnamed-uvm_set_before_get_dap#(T)"):
        uvm_set_get_dap_base.__init__(self, name)
        self.m_set = False
        self.m_value = None

    #   // Group: Set/Get Interface
    #
    #   // Function: set
    #   // Updates the value stored within the DAP.
    #   //
    def set(self, value):
        self.m_set = True
        self.m_value = value

    #   // Function: try_set
    #   // Attempts to update the value stored within the DAP.
    #   //
    #   // ~try_set~ will always return a 1.
    #   virtual function bit try_set(T value);
    #      set(value);
    #      return 1;
    #   endfunction : try_set
    #

    #   // Function: get
    #   // Returns the current value stored within the DAP.
    #   //
    #   // If 'get' is called before a call to <set> or <try_set>, then
    #   // an error will be reported.
    def get(self):
        if self.m_set is False:
            uvm_error("UVM/SET_BEFORE_GET_DAP/NO_SET", sv.sformatf(ERR_MSG1, self.get_full_name()))
        return self.m_value

    #
    #   // Function: try_get
    #   // Attempts to retrieve the current value stored within the DAP
    #   //
    #   // If the value has not been 'set', then try_get will return a 0,
    #   // otherwise it will return a 1, and set ~value~ to the current
    #   // value stored within the DAP.
    def try_get(self, value):
        uvm_check_output_args([value])
        if self.m_set is False:
            return 0
        else:
            value.append(self.m_value)
            return 1

    #
    #   // Group: Introspection
    #   //
    #   // The ~uvm_set_before_get_dap~ cannot support the standard UVM
    #   // instrumentation methods (~copy~, ~clone~, ~pack~ and
    #   // ~unpack~), due to the fact that they would potentially
    #   // violate the access policy.
    #   //
    #   // A call to any of these methods will result in an error.
    #
    #   virtual function void do_copy(uvm_object rhs);
    #      `uvm_error("UVM/SET_BEFORE_GET_DAP/CPY",
    #                 "'copy()' is not supported for 'uvm_set_before_get_dap#(T)'")
    #   endfunction : do_copy
    #
    #   virtual function void do_pack(uvm_packer packer);
    #      `uvm_error("UVM/SET_BEFORE_GET_DAP/PCK",
    #                 "'pack()' is not supported for 'uvm_set_before_get_dap#(T)'")
    #   endfunction : do_pack
    #
    #   virtual function void do_unpack(uvm_packer packer);
    #      `uvm_error("UVM/SET_BEFORE_GET_DAP/UPK",
    #                 "'unpack()' is not supported for 'uvm_set_before_get_dap#(T)'")
    #   endfunction : do_unpack
    #
    #   // Group- Reporting
    #
    #   // Function- convert2string
    #   virtual function string convert2string();
    #      if (m_set)
    #        return $sformatf("(%s) %0p [SET]", `uvm_typename(m_value), m_value);
    #      else
    #        return $sformatf("(%s) %0p [UNSET]", `uvm_typename(m_value), m_value);
    #   endfunction : convert2string
    #
    #   // Function- do_print
    #   virtual function void do_print(uvm_printer printer);
    #      super.do_print(printer);
    #      printer.print_field_int("set_state", m_set, $bits(m_set));
    #      printer.print_generic("value",
    #                            `uvm_typename(m_value),
    #                            0,
    #                            $sformatf("%0p", m_value));
    #
    #   endfunction : do_print
    #
    #endclass // uvm_set_before_get_dap


uvm_object_utils(uvm_set_before_get_dap)
