import React, { useState, useMemo } from 'react';
import {
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TablePagination,
  Paper,
  TextField,
  InputAdornment,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import LoadingSpinner from '../common/LoadingSpinner';
import EmptyState from '../common/EmptyState';

const ReusableDataTable = ({
  columns,
  data = [],
  searchKey,
  searchPlaceholder = 'Search records...',
  filterOptions = [],
  dateFilterKey,
  loading = false,
  emptyTitle = 'No records found',
  emptyDescription = 'There are no items matching your criteria.',
  onRowClick
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Pagination State (default 10)
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Sorting State
  const [sortKey, setSortKey] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setPage(0);
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value
    }));
    setPage(0);
  };

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortOrder('asc');
    }
  };

  // Filter & Sort Logic
  const filteredSortedData = useMemo(() => {
    let result = [...data];

    // 1. Text Search
    if (searchQuery && searchKey) {
      result = result.filter((item) => {
        const value = item[searchKey];
        return value && String(value).toLowerCase().includes(searchQuery.toLowerCase());
      });
    }

    // 2. Custom Select Filters
    Object.keys(filters).forEach((key) => {
      const val = filters[key];
      if (val && val !== 'All') {
        result = result.filter((item) => String(item[key]) === String(val));
      }
    });

    // 3. Date Filters
    if (dateFilterKey && (startDate || endDate)) {
      result = result.filter((item) => {
        const itemDateStr = item[dateFilterKey];
        if (!itemDateStr) return false;

        const itemDate = new Date(itemDateStr);

        if (startDate) {
          const start = new Date(startDate);
          start.setHours(0, 0, 0, 0);
          if (itemDate < start) return false;
        }

        if (endDate) {
          const end = new Date(endDate);
          end.setHours(23, 59, 59, 999);
          if (itemDate > end) return false;
        }

        return true;
      });
    }

    // 4. Sorting
    if (sortKey) {
      result.sort((a, b) => {
        const valA = a[sortKey];
        const valB = b[sortKey];

        if (valA === undefined || valA === null) return 1;
        if (valB === undefined || valB === null) return -1;

        if (typeof valA === 'number' && typeof valB === 'number') {
          return sortOrder === 'asc' ? valA - valB : valB - valA;
        }

        return sortOrder === 'asc'
          ? String(valA).localeCompare(String(valB))
          : String(valB).localeCompare(String(valA));
      });
    }

    return result;
  }, [data, searchQuery, searchKey, filters, startDate, endDate, dateFilterKey, sortKey, sortOrder]);

  const paginatedData = useMemo(() => {
    const start = page * rowsPerPage;
    return filteredSortedData.slice(start, start + rowsPerPage);
  }, [filteredSortedData, page, rowsPerPage]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      {/* Controls: Search, Select Filters, Date Pickers */}
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 1.5,
          mb: 2.5,
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, flex: 1, minWidth: 260 }}>
          {searchKey && (
            <TextField
              size="small"
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={handleSearchChange}
              sx={{ flexGrow: 1, maxWidth: 360, minWidth: 220 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" fontSize="small" />
                  </InputAdornment>
                ),
                style: { borderRadius: 10, backgroundColor: '#ffffff', fontSize: '0.85rem' }
              }}
            />
          )}

          {filterOptions.map((fOpt) => (
            <FormControl key={fOpt.key} size="small" sx={{ minWidth: 160 }}>
              <InputLabel id={`filter-label-${fOpt.key}`} sx={{ fontSize: '0.85rem' }}>{fOpt.label}</InputLabel>
              <Select
                labelId={`filter-label-${fOpt.key}`}
                value={filters[fOpt.key] || 'All'}
                label={fOpt.label}
                onChange={(e) => handleFilterChange(fOpt.key, e.target.value)}
                sx={{ borderRadius: 2.5, backgroundColor: '#ffffff', fontSize: '0.85rem' }}
              >
                <MenuItem value="All" sx={{ fontSize: '0.85rem' }}>All {fOpt.label}s</MenuItem>
                {fOpt.options.map((opt) => (
                  <MenuItem key={opt} value={opt} sx={{ fontSize: '0.85rem' }}>
                    {opt}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          ))}
        </Box>

        {dateFilterKey && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TextField
              type="date"
              size="small"
              label="Start Date"
              value={startDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                setPage(0);
              }}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 130 }}
              InputProps={{ style: { borderRadius: 10, backgroundColor: '#ffffff', fontSize: '0.82rem' } }}
            />
            <Typography variant="caption" color="text.secondary">to</Typography>
            <TextField
              type="date"
              size="small"
              label="End Date"
              value={endDate}
              onChange={(e) => {
                setEndDate(e.target.value);
                setPage(0);
              }}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: 130 }}
              InputProps={{ style: { borderRadius: 10, backgroundColor: '#ffffff', fontSize: '0.82rem' } }}
            />
          </Box>
        )}
      </Box>

      {/* Main Table */}
      {loading ? (
        <Paper elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3, overflow: 'hidden' }}>
          <LoadingSpinner message="Querying live database records..." />
        </Paper>
      ) : filteredSortedData.length === 0 ? (
        <EmptyState title={emptyTitle} description={emptyDescription} />
      ) : (
        <Paper elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3, overflow: 'hidden', bgcolor: '#ffffff' }}>
          <TableContainer>
            <Table sx={{ minWidth: 650 }}>
              <TableHead sx={{ bgcolor: '#f8fafc' }}>
                <TableRow>
                  {columns.map((col) => (
                    <TableCell
                      key={col.id}
                      align={col.align || 'left'}
                      sx={{
                        fontWeight: 700,
                        color: '#475569',
                        fontSize: '0.78rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        py: 1.6,
                        borderBottom: '1px solid #e2e8f0',
                        cursor: col.sortable ? 'pointer' : 'default',
                        userSelect: 'none'
                      }}
                      onClick={() => col.sortable && handleSort(col.id)}
                    >
                      <Box display="inline-flex" alignItems="center">
                        {col.label}
                        {col.sortable && sortKey === col.id && (
                          <Box component="span" sx={{ ml: 0.5 }}>
                            {sortOrder === 'asc' ? (
                              <ArrowUpwardIcon fontSize="inherit" />
                            ) : (
                              <ArrowDownwardIcon fontSize="inherit" />
                            )}
                          </Box>
                        )}
                      </Box>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedData.map((row, index) => (
                  <TableRow
                    key={row.id || index}
                    hover
                    onClick={() => onRowClick && onRowClick(row)}
                    sx={{
                      cursor: onRowClick ? 'pointer' : 'default',
                      transition: 'background-color 0.15s',
                      '&:hover': { bgcolor: '#f8fafc' },
                      '&:last-child td, &:last-child th': { border: 0 }
                    }}
                  >
                    {columns.map((col) => (
                      <TableCell
                        key={col.id}
                        align={col.align || 'left'}
                        sx={{
                          py: 1.5,
                          fontSize: '0.85rem',
                          borderBottom: '1px solid #f1f5f9'
                        }}
                      >
                        {col.render ? col.render(row) : row[col.id]}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={filteredSortedData.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            sx={{
              borderTop: '1px solid #e2e8f0',
              '.MuiTablePagination-selectLabel, .MuiTablePagination-displayedRows': {
                fontSize: '0.8rem',
                color: '#64748b'
              }
            }}
          />
        </Paper>
      )}
    </Box>
  );
};

export default ReusableDataTable;
